from charm.toolbox.pairinggroup import *
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
import re


class MaabeRW15(ABEncMultiAuth):
    """
    Efficient Statically-Secure Large-Universe Multi-Authority Attribute-Based Encryption
    Rouselakis - Waters
    """

    def __init__(self, group, verbose=False):
        ABEncMultiAuth.__init__(self)
        self.group = group
        self.util = SecretUtil(group, verbose)

    def setup(self, g1, g2):
        egg = pair(g1, g2)
        H = lambda x: self.group.hash(x, G2)
        F = lambda x: self.group.hash(x, G2)
        gp = {'g1': g1, 'g2': g2, 'egg': egg, 'H': H, 'F': F}
        return gp

    def unpack_attribute(self, attribute):
        """
        Unpacks an attribute in attribute name, authority name and index
        :param attribute: The attribute to unpack
        :return: The attribute name, authority name and the attribute index, if present.
         group = PairingGroup('SS512')
         maabe = MaabeRW15(group)
         maabe.unpack_attribute('STUDENT@UT')
        ('STUDENT', 'UT', None)
         maabe.unpack_attribute('STUDENT@UT_2')
        ('STUDENT', 'UT', '2')
        """
        parts = re.split(r"[@_]", attribute)
        assert len(parts) > 1, "No @ char in [attribute@authority] name"
        return parts[0], parts[1], None if len(parts) < 3 else parts[2]

    def authsetup(self, gp, name):
        """
        Setup an attribute authority.
        :param gp: The global parameters
        :param name: The name of the authority
        :return: The public and private key of the authority
        """
        alpha, y = self.group.random(), self.group.random()
        egga = gp['egg'] ** alpha
        gy = gp['g1'] ** y
        pk = {'name': name, 'egga': egga, 'gy': gy}
        sk = {'name': name, 'alpha': alpha, 'y': y}
        return pk, sk

    def keygen(self, gp, sk, gid, attribute):
        """
        Generate a user secret key for the attribute.
        :param gp: The global parameters.
        :param sk: The secret key of the attribute authority.
        :param gid: The global user identifier.
        :param attribute: The attribute.
        :return: The secret key for the attribute for the user with identifier gid.
        """
        _, auth, _ = self.unpack_attribute(attribute)
        assert sk['name'] == auth, "Attribute %s does not belong to authority %s" % (attribute, sk['name'])
        t = self.group.random()
        H = lambda x: self.group.hash(x, G2)
        F = lambda x: self.group.hash(x, G2)
        K = gp['g2'] ** sk['alpha'] * H(gid) ** sk['y'] * F(attribute) ** t
        KP = gp['g1'] ** t
        return {'K': K, 'KP': KP}

    def multiple_attributes_keygen(self, gp, sk, gid, attributes):
        """
        Generate a dictionary of secret keys for a user for a list of attributes.
        :param gp: The global parameters.
        :param sk: The secret key of the attribute authority.
        :param gid: The global user identifier.
        :param attributes: The list of attributes.
        :return: A dictionary with attribute names as keys, and secret keys for the attributes as values.
        """
        uk = {}
        for attribute in attributes:
            uk[attribute] = self.keygen(gp, sk, gid, attribute)
        return uk

    def encrypt(self, gp, pks, message, policy_str):
        """
        Encrypt a message under an access policy
        :param gp: The global parameters.
        :param pks: The public keys of the relevant attribute authorities, as dict from authority name to public key.
        :param message: The message to encrypt.
        :param policy_str: The access policy to use.
        :return: The encrypted message.
        """
        s = self.group.random()  # secret to be shared
        w = self.group.init(ZR, 0)  # 0 to be shared
        policy = self.util.createPolicy(policy_str)
        attribute_list = self.util.getAttributeList(policy)
        secret_shares = self.util.calculateSharesDict(s, policy)  # These are correctly set to be exponents in Z_p
        zero_shares = self.util.calculateSharesDict(w, policy)
        C0 = message * (gp['egg'] ** s)
        C1, C2, C3, C4 = {}, {}, {}, {}
        F = lambda x: self.group.hash(x, G2)
        for i in attribute_list:
            attribute_name, auth, _ = self.unpack_attribute(i)
            attr = "%s@%s" % (attribute_name, auth)
            tx = self.group.random()
            C1[i] = gp['egg'] ** secret_shares[i] * pks[auth]['egga'] ** tx
            C2[i] = gp['g1'] ** (-tx)
            C3[i] = pks[auth]['gy'] ** tx * gp['g1'] ** zero_shares[i]
            C4[i] = F(attr) ** tx
        return {'policy': policy_str, 'C0': C0, 'C1': C1, 'C2': C2, 'C3': C3, 'C4': C4}

    def decrypt(self, gp, sk, ct):
        """
        Decrypt the ciphertext using the secret keys of the user.
        :param gp: The global parameters.
        :param sk: The secret keys of the user.
        :param ct: The ciphertext to decrypt.
        :return: The decrypted message.
        :raise Exception: When the access policy can not be satisfied with the user's attributes.
        """
        policy = self.util.createPolicy(ct['policy'])
        coefficients = self.util.getCoefficients(policy)
        pruned_list = self.util.prune(policy, sk['keys'].keys())
        if not pruned_list:
            raise Exception("You don't have the required attributes for decryption!")
        B = self.group.init(GT, 1)
        for i in range(len(pruned_list)):
            x = pruned_list[i].getAttribute()  # without the underscore
            y = pruned_list[i].getAttributeAndIndex()  # with the underscore
            H = lambda x: self.group.hash(x, G2)
            B *= (ct['C1'][y] * pair(ct['C2'][y], sk['keys'][x]['K']) * pair(ct['C3'][y], H(sk['GID'])) * pair(
                sk['keys'][x]['KP'], ct['C4'][y])) ** coefficients[y]
        return ct['C0'] / B

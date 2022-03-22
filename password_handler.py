from cryptography.fernet import Fernet 
import json

class PasswordHandler:
	def __init__(self, passFile='passwords.json', keyFile='key.key'):
		self.filename = passFile
		try:
			with open(keyFile, 'rb') as fk:
				self.key = fk.read()
		except:
			self.key = Fernet.generate_key()
			with open(keyFile, 'wb') as fk:
				fk.write(self.key)
		f = Fernet(self.key)
		try:
			with open(self.filename, 'rb') as fp:
				encrypted_passwords = fp.read()
			self.passwords = f.decrypt(encrypted_passwords)
			self.passwords = json.loads(self.passwords)
		except:
			open(self.filename, 'wb').close()
			self.passwords = {}

	def getAll(self):
		return self.passwords

	def getPassword(self, account):
		if account in self.passwords.keys():
			return self.passwords[account]
		else:
			return None

	def storePassword(self, account, password):
		self.passwords[account] = password
		self.storeToFile()

	def changeAccountName(self, oldAcc, newAcc):
		if oldAcc in self.passwords.keys():
			self.passwords[newAcc] = self.passwords.pop(oldAcc)
			self.storeToFile()

	def storeToFile(self):
		j = json.dumps(self.passwords).encode()
		f = Fernet(self.key)
		ep = f.encrypt(j)
		with open(self.filename, 'wb') as fp:
			fp.write(ep)

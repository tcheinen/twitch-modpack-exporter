import os
import ctypes.wintypes
import json
import zipfile

CSIDL_PERSONAL = 5       # My Documents
SHGFP_TYPE_CURRENT = 0   # Get current, not default value

buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
instances_folder = os.path.join(buf.value, "Curse\\Minecraft\\Instances")
instances = dict(enumerate(os.listdir(instances_folder)))

for k, v in instances.items():
	print("[{}] {}".format(k, v))
chosen = instances[int(input("Type a number to select which modpack you want to export:  "))]
instance_path = os.path.join(instances_folder, chosen, "minecraftinstance.json")

with open(instance_path) as f:
	instance_data = json.loads(f.read())

manifest = {}
modlist = {}

manifest["name"] = instance_data["name"]
manifest["author"] = instance_data["customAuthor"]

manifest["version"] = 1
manifest["manifestType"] = "minecraftModpack"
manifest["manifestVersion"] = 1
manifest["overrides"] = "overrides"
manifest["files"] = []
manifest["minecraft"] = {}
manifest["minecraft"]["version"] = instance_data["gameVersion"]
manifest["minecraft"]["modLoaders"] = [{"id": instance_data["baseModLoader"]["name"],"primary": True}]
for i in instance_data["installedAddons"]:
	file = {}
	file["projectID"] = i["addonID"]
	file["fileID"] = i["installedFile"]["id"]
	file["require"] = True
	manifest["files"].append(file)

output = zipfile.ZipFile("{}.zip".format(manifest["name"]),"w")
output.writestr("manifest.json", json.dumps(manifest, sort_keys=True, indent=4, separators=(',', ': ')))

for root, dirs, files in os.walk(os.path.join(instances_folder, chosen, "config")):
	cfgpath = os.path.relpath(root, os.path.join(instances_folder, chosen))
	for i in files:
		output.write(os.path.join(root, i),os.path.join("overrides", cfgpath, i))
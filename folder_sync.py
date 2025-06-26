import os
import sys
import time
import hashlib
import shutil
from datetime import datetime


# Logs a timestamped message to both the console and a log file.
def log_message(logger, message):
	timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
	full_message = f"{timestamp} {message}"
	print(full_message)
	logger.write(full_message + '\n')
	logger.flush()


# Calculates the MD5 hash of a file to check for changes. Returns None if error occurs.
def calculate_md5(file_path):
	hash_md5 = hashlib.md5()
	try:
		with open(file_path, "rb") as f:
			for chunk in iter(lambda: f.read(4096), b""):
				hash_md5.update(chunk)
		return hash_md5.hexdigest()
	except Exception:
		return None


# Copies a file from source to destination, logging the action. Handles errors.
def copy_file(src_path, dest_path, logger):
	try:
		shutil.copy2(src_path, dest_path)
		log_message(logger, f"Copied file: {src_path} -> {dest_path}")
	except Exception as e:
		log_message(logger, f"Error copying file {src_path} to {dest_path}: {str(e)}")


# Removes a file, logging the action. Handles errors.
def remove_file(path, logger):
	try:
		os.remove(path)
		log_message(logger, f"Removed file: {path}")
	except Exception as e:
		log_message(logger, f"Error removing file {path}: {str(e)}")


# Removes a directory and its contents, logging the action. Handles errors.
def remove_dir(path, logger):
	try:
		shutil.rmtree(path)
		log_message(logger, f"Removed directory: {path}")
	except Exception as e:
		log_message(logger, f"Error removing directory {path}: {str(e)}")


# Creates missing directories in the replica, logging the action. Handles errors.
def create_missing_directories(source, replica, logger):
	for root, dirs, files in os.walk(source):
		rel_path = os.path.relpath(root, source)
		replica_root = replica if rel_path == "." else os.path.join(replica, rel_path)
		if not os.path.exists(replica_root):
			try:
				os.makedirs(replica_root)
				log_message(logger, f"Created directory: {replica_root}")
			except Exception as e:
				log_message(logger, f"Error creating directory {replica_root}: {str(e)}")


# Copies or updates files from source to replica, logging the action. Handles errors.
def copy_or_update_files(source, replica, logger):
	for root, dirs, files in os.walk(source):
		rel_path = os.path.relpath(root, source)
		replica_root = replica if rel_path == "." else os.path.join(replica, rel_path)

		for file in files:
			src_file = os.path.join(root, file)
			replica_file = os.path.join(replica_root, file)
			if not os.path.exists(replica_file):
				copy_file(src_file, replica_file, logger)
			else:
				src_hash = calculate_md5(src_file)
				replica_hash = calculate_md5(replica_file)
				if src_hash != replica_hash:
					copy_file(src_file, replica_file, logger)


# Removes files and directories in the replica that do not exist in the source, logging the action.
def remove_extra_files_and_dirs(source, replica, logger):
	for root, dirs, files in os.walk(replica, topdown=False):
		rel_path = os.path.relpath(root, replica)
		source_root = source if rel_path == "." else os.path.join(source, rel_path)

		for file in files:
			replica_file = os.path.join(root, file)
			source_file = os.path.join(source_root, file)
			if not os.path.exists(source_file):
				remove_file(replica_file, logger)

		for dir in dirs:
			replica_dir = os.path.join(root, dir)
			source_dir = os.path.join(source_root, dir)
			if not os.path.exists(source_dir):
				remove_dir(replica_dir, logger)


# Synchronizes the source and replica folders by creating missing directories,
#copying or updating files, and removing extra files and directories.
def sync_folders(source, replica, logger):
	create_missing_directories(source, replica, logger)
	copy_or_update_files(source, replica, logger)
	remove_extra_files_and_dirs(source, replica, logger)


# Main function to handle command line arguments and initiate synchronization.
def main():
	if len(sys.argv) != 6:
		return

	source_folder = sys.argv[1]
	replica_folder = sys.argv[2]
	try:
		interval = int(sys.argv[3])
		sync_count = int(sys.argv[4])
	except ValueError:
		print("Interval and count must be integers.")
		return

	log_file_path = os.path.abspath(sys.argv[5])

	try:
		with open(log_file_path, 'a', buffering=1) as logger:  # line-buffered
			for i in range(sync_count):
				log_message(logger, f"--- Synchronization {i + 1}/{sync_count} started ---")
				sync_folders(source_folder, replica_folder, logger)
				log_message(logger, f"--- Synchronization {i + 1}/{sync_count} finished ---")
				if i != sync_count - 1:
					time.sleep(interval)
	except Exception as e:
		print(f"Fatal error: {e}")


if __name__ == "__main__":
	main()

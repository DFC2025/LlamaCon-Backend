import os
import pathlib
import modal

app = modal.App()

volume = modal.Volume.from_name("Pocket_flow")


@app.function(volumes={"/PocketFlow-Tutorial-Codebase-Knowledge": volume})
def g():
    
    # walk through the directory and print the files
    # get the current working directory
    # change to root/PocketFlow-Tutorial-Codebase-Knowledge/PocketFlow-Tutorial-Codebase-Knowledge
    # print(f"Files in current working directory: {os.listdir(os.getcwd())}")
    return os.listdir(os.getcwd())



# @app.local_entrypoint()
# def main():
#     g.remote()  # 1. container for `g` starts
# # 
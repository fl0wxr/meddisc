'''
    Description:
        Read/write related functionality.
'''


import pydicom as dicom
from PIL import Image
import numpy as np
import shutil
import os
import json
from glob import glob
import hashlib


class rwdcm:
    '''
        Description:
            Can read and write multiple files on a directory.
    '''

    def __init__(self, in_dp: str, out_dp: str):

        self.modifiable_file_extension_names = \
        [
            'dcm',
            'dcM',
            'dCm',
            'dCM',
            'Dcm',
            'DcM',
            'DCm',
            'DCM'
        ]

        self.SAFETY_SWITCH = True
        if not self.SAFETY_SWITCH:
            print('W: Safety switch is off. Output directory can now be deleted.')

        if in_dp[-1] != '/': in_dp = in_dp + '/'
        self.raw_data_dp = in_dp
        self.raw_dicom_paths = sorted(self.get_dicom_paths(data_dp = self.raw_data_dp))
        self.clean_data_dp = out_dp + '/' + 'de-identified-files/'

        already_cleaned_dicom_paths = self.get_dicom_paths(data_dp = self.clean_data_dp)
        self.hashes_of_already_converted_files = [already_cleaned_dicom_path.split('/')[-1].split('.')[0] for already_cleaned_dicom_path in already_cleaned_dicom_paths]

        self.n_dicom_files = len(self.raw_dicom_paths)

        print('\nTotal number of DICOM files existing inside the input directory:\n%d'%(self.n_dicom_files))
        print('---', end = 2 * '\n')

        self.DICOM_IDX = -1

    def __next__(self):

        self.DICOM_IDX += 1
        if self.DICOM_IDX <= self.n_dicom_files - 1:
            self.raw_dicom_path = self.raw_dicom_paths[self.DICOM_IDX]
            print('List index:', self.DICOM_IDX)
            print('---\n')
            return True
        else:
            return False

    def get_dicom_paths(self, data_dp):

        dicom_paths = []
        for extension_name in self.modifiable_file_extension_names:
            dicom_paths += \
            (
                glob\
                (
                    pathname = data_dp + '**/*.' + extension_name,
                    recursive = True
                )
            )

        return dicom_paths

    def parse_file(self):

        self.input_dicom_hash = hashlib.sha256(self.raw_dicom_path.encode('UTF-8')).hexdigest()

        if self.input_dicom_hash in self.hashes_of_already_converted_files:
            return False
        else:
            dcm = dicom.dcmread(self.raw_dicom_path)
            print('Parsed\n%s'%(self.raw_dicom_path))
            return dcm

    def export_processed_file(self, dcm):

        self.clean_dicom_dp = self.clean_data_dp + str(dcm['00100020'].value) + '/' + str(dcm['00080060'].value) + '/' + str(dcm['00200011'].value)
        if not os.path.exists(self.clean_dicom_dp):
            os.makedirs(self.clean_dicom_dp)

        ## Clean DICOM file example:
        ## self.clean_data_dp + 'de-identified-files/<TAG-00100020>/<TAG-00080060>/<TAG-00200011>/364a954efb2e4489f1fb5878c57aa1bbbbc97ffe00f236247aeaab22caa284ee.dcm'
        clean_dicom_fp = self.clean_dicom_dp + '/' + self.input_dicom_hash + '.dcm'

        print('Exporting file at\n%s'%(clean_dicom_fp))

        dcm.save_as(clean_dicom_fp)

    def export_session(self, session):

        with open(self.clean_data_dp + '/session.json', 'w') as file:
            json.dump(session, file)
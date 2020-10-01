import math


class FileUtil:
    @staticmethod
    def gen_metadata(secret_len: int, max_len: int, ext: str) -> list:
        metadata = ''
        secret_len_bitsize = math.ceil(math.log(max_len, 2))
        metadata += bin(secret_len).lstrip('0b').rjust(secret_len_bitsize, '0')

        if len(ext) == 3:
            metadata += '00000000'

        for char in ext:
            char_bin = bin(ord(char)).lstrip('0b').rjust(8, '0')
            metadata += char_bin

        return list(map(int, metadata))

    @staticmethod
    def get_metadata_len(filesize: int) -> int:
        secret_len_bitsize = math.ceil(math.log(filesize, 2))
        return secret_len_bitsize + 32

    @staticmethod
    def binary_to_dec(bin_array: list) -> int:
        string_array = map(str, bin_array)
        dec = ''.join(string_array)
        dec = '0b' + dec
        return int(dec, 2)


if __name__ == "__main__":
    print(FileUtil.gen_metadata(8, 17, 'doc'))

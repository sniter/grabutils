import os


class TextFileUtils:

    @staticmethod
    def partition(file: str, partitions: int = 0) -> list:
        """Partition text file into partitions
        Parameters
        ----------
        file : str
            file to partition
        partitions : int
            num partitions, by default equal `os.cpu_count()`

        Returns
        -------
        list
            List of created partitions

        """
        if int(partitions) <= 0:
            partitions = os.cpu_count()

        files = [
            f'{file}.{partition:04d}'
            for partition in range(partitions)
        ]

        with open(file, 'r') as lines:
            for line_no, line in enumerate(lines, start=1):
                partition = line_no % partitions
                with open(files[partition], 'a') as file_partition:
                    file_partition.write(file)

        return files

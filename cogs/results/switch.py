import re

from .types import Module, ResultCode, UNKNOWN_MODULE, NO_RESULTS_FOUND

"""
This file contains all currently known Switch result and error codes. 
There may be inaccuracies here; we'll do our best to correct them 
when we find out more about them.

A result code is a 32-bit integer returned when calling various commands in the
Switch's operating system, Horizon. Its breaks down like so:

 Bits | Description
-------------------
00-08 | Module
09-21 | Description

Module: A value indicating who raised the error or returned the result.
Description: A value indicating exactly what happened.

Unlike the 3DS, the Nintendo Switch does not provide a 'summary' or 'level'
field in result codes, so some artistic license was taken here to repurpose those
fields in our ResultCode class to add additional information from sources
such as Atmosphere's libvapours and the Switchbrew wiki.

To add a module so the code understands it, simply add a new module number
to the 'modules' dictionary, with a Module variable as the value. If the module
has no known error codes, simply add a dummy Module instead (see the dict for
more info). See the various module variables for a more in-depth example
 on how to make one.

Once you've added a module, or you want to add a new result code to an existing
module, add a new description value (for Switch it's the final set of 4 digits after any dashes)
as the key, and a ResultCode variable with a text description of the error or result.
You can also add a second string to the ResultCode to designate a support URL if
one exists. Not all results or errors have support webpages.

Simple example of adding a module with a sample result code:
test = Module('test', {
    5: ResultCode('test', 'https://example.com')
})

modules = {
    9999: test
}

Sources used to compile these results and information:
https://switchbrew.org/wiki/Error_codes
https://github.com/Atmosphere-NX/Atmosphere/tree/master/libraries/libvapours/include/vapours/results
"""

kernel = Module('kernel', {
    7: ResultCode('Out of sessions.'),
    14: ResultCode('Invalid argument.'),
    33: ResultCode('Not implemented.'),
    54: ResultCode('Stop processing exception.'),
    57: ResultCode('No synchronization object.'),
    59: ResultCode('Termination requested.'),
    70: ResultCode('No event.'),
    101: ResultCode('Invalid size.'),
    102: ResultCode('Invalid address.'),
    103: ResultCode('Out of resources.'),
    104: ResultCode('Out of memory.'),
    105: ResultCode('Out of handles.'),
    106: ResultCode('Invalid current memory state or permissions.'),
    108: ResultCode('Invalid new memory permissions.'),
    110: ResultCode('Invalid memory region.'),
    112: ResultCode('Invalid thread priority.'),
    113: ResultCode('Invalid processor core ID.'),
    114: ResultCode('Invalid handle.'),
    115: ResultCode('Invalid pointer.'),
    116: ResultCode('Invalid combination.'),
    117: ResultCode('Timed out.'),
    118: ResultCode('Cancelled.'),
    119: ResultCode('Out of range.'),
    120: ResultCode('Invalid enum value.'),
    121: ResultCode('Not found.'),
    122: ResultCode('Busy or already registered.'),
    123: ResultCode('Session closed.'),
    124: ResultCode('Not handled.'),
    125: ResultCode('Invalid state.'),
    126: ResultCode('Reserved used.'),
    127: ResultCode('Not supported.'),
    128: ResultCode('Debug.'),
    129: ResultCode('Thread not owned.'),
    131: ResultCode('Port closed.'),
    132: ResultCode('Limit reached.'),
    133: ResultCode('Invalid memory pool.'),
    258: ResultCode('Receive list broken.'),
    259: ResultCode('Out of address space.'),
    260: ResultCode('Message too large.'),
    517: ResultCode('Invalid process ID.'),
    518: ResultCode('Invalid thread ID.'),
    519: ResultCode('Invalid thread ID (svcGetDebugThreadParam).'),
    520: ResultCode('Process terminated.')
})

fs = Module('fs', {
    1: ResultCode('Path not found.'),
    2: ResultCode('Path already exists.'),
    7: ResultCode('Target locked (already in use).'),
    8: ResultCode('Directory not empty.'),
    35: ResultCode('Not enough free space on CAL0 partition.'),
    36: ResultCode('Not enough free space on SAFE partition.'),
    37: ResultCode('Not enough free space on USER partition.'),
    38: ResultCode('Not enough free space on SYSTEM partition.'),
    39: ResultCode('Not enough free space on SD card.'),
    50: ResultCode('NCA is older than version 3, or NCA SDK version is < 0.11.0.0.'),
    60: ResultCode('Mount name already exists.'),
    1001: ResultCode('Process does not have RomFS.'),
    1002: ResultCode('Target not found.'),
    2001: ResultCode('SD card not present.'),
    2520: ResultCode('Game Card is not inserted.'),
    2522: ResultCode('Attempted to process an AsicHandler command in initial mode.'),
    2540: ResultCode('Attempted to read from the secure Game Card partition in normal mode.'),
    2541: ResultCode('Attempted to read from the normal Game Card partition in secure mode.'),
    2542: ResultCode('Attempted a read that spanned both the normal and secure Game Card partitions.'),
    2544: ResultCode('Game Card initial data hash doesn\'t match the initial data hash in the card header.'),
    2545: ResultCode('Game Card initial data reserved area is not all zeroes.'),
    2546: ResultCode('Game Card certificate kek index doesn\'t match card header kek index.'),
    2551: ResultCode('Unable to read card header on Game Card initialization.'),
    2565: ResultCode('Encountered SDMMC error in write operation.'),
    2600: ResultCode('Attempted to switch Lotus state machine to secure mode from a mode other than normal mode.'),
    2601: ResultCode('Attempted to switch Lotus state machine to normal mode from a mode other than initial mode.'),
    2602: ResultCode('Attempted to switch Lotus state machine to write mode from a mode other than normal mode.'),
    2634: ResultCode('Error processing Lotus command SetUserAsicFirmware.'),
    2637: ResultCode('Error processing Lotus command GetAsicCert.'),
    2640: ResultCode('Error processing Lotus command SetEmmcEmbeddedSocCertificate.'),
    2645: ResultCode('Error processing Lotus command GetAsicEncryptedMessage.'),
    2646: ResultCode('Error processing Lotus command SetLibraryEncryptedMessage.'),
    2651: ResultCode('Error processing Lotus command GetAsicAuthenticationData.'),
    2652: ResultCode('Error processing Lotus command SetAsicAuthenticationDataHash.'),
    2653: ResultCode('Error processing Lotus command SetLibraryAuthenticationData.'),
    2654: ResultCode('Error processing Lotus command GetLibraryAuthenticationDataHash.'),
    2657: ResultCode('Error processing Lotus command ExchangeRandomValuesInSecureMode.'),
    2668: ResultCode('Error calling nn::gc::detail::GcCrypto::GenerateRandomBytes.'),
    2671: ResultCode('Error processing Lotus command ReadAsicRegister.'),
    2672: ResultCode('Error processing Lotus command GetGameCardIdSet.'),
    2674: ResultCode('Error processing Lotus command GetCardHeader.'),
    2676: ResultCode('Error processing Lotus command GetCardKeyArea.'),
    2677: ResultCode('Error processing Lotus command ChangeDebugMode.'),
    2678: ResultCode('Error processing Lotus command GetRmaInformation.'),
    2692: ResultCode('Tried sending Lotus card command Refresh when not in secure mode.'),
    2693: ResultCode('Tried sending Lotus card command when not in correct mode.'),
    2731: ResultCode('Error processing Lotus card command ReadId1.'),
    2732: ResultCode('Error processing Lotus card command ReadId2.'),
    2733: ResultCode('Error processing Lotus card command ReadId3.'),
    2735: ResultCode('Error processing Lotus card command ReadPage.'),
    2737: ResultCode('Error processing Lotus card command WritePage.'),
    2738: ResultCode('Error processing Lotus card command Refresh.'),
    2742: ResultCode('Error processing Lotus card command ReadCrc.'),
    2743: ResultCode('Error processing Lotus card command Erase or UnlockForceErase.'),
    2744: ResultCode('Error processing Lotus card command ReadDevParam.'),
    2745: ResultCode('Error processing Lotus card command WriteDevParam.'),
    2904: ResultCode('Id2Normal did not match the value in the buffer returned by ChangeDebugMode.'),
    2905: ResultCode('Id1Normal did not match Id1Writer when switching gamecard to write mode.'),
    2906: ResultCode('Id2Normal did not match Id2Writer when switching gamecard to write mode.'),
    2954: ResultCode('Invalid Game Card handle.'),
    2960: ResultCode('Invalid gamecard handle when opening normal gamecard partition.'),
    2961: ResultCode('Invalid gamecard handle when opening secure gamecard partition.'),
    3001: ResultCode('Not implemented.'),
    3002: ResultCode('Unsupported version.'),
    3003: ResultCode('File or directory already exists.'),
    3005: ResultCode('Out of range.'),
    3100: ResultCode('System partition not ready.'),
    3201: ResultCode('Memory allocation failure related to FAT filesystem code.'),
    3203: ResultCode('Memory allocation failure related to FAT filesystem code.'),
    3204: ResultCode('Memory allocation failure related to FAT filesystem code.'),
    3206: ResultCode('Memory allocation failure related to FAT filesystem code.'),
    3208: ResultCode('Memory allocation failure related to FAT filesystem code.'),
    3211: ResultCode('Allocation failure in FileSystemAccessorA.'),
    3212: ResultCode('Allocation failure in FileSystemAccessorB.'),
    3213: ResultCode('Allocation failure in ApplicationA.'),
    3215: ResultCode('Allocation failure in BisA.'),
    3216: ResultCode('Allocation failure in BisB.'),
    3217: ResultCode('Allocation failure in BisC.'),
    3218: ResultCode('Allocation failure in CodeA.'),
    3219: ResultCode('Allocation failure in ContentA.'),
    3220: ResultCode('Allocation failure in ContentStorageA.'),
    3221: ResultCode('Allocation failure in ContentStorageB.'),
    3222: ResultCode('Allocation failure in DataA.'),
    3223: ResultCode('Allocation failure in DataB.'),
    3224: ResultCode('Allocation failure in DeviceSaveDataA.'),
    3225: ResultCode('Allocation failure in GameCardA'),
    3226: ResultCode('Allocation failure in GameCardB'),
    3227: ResultCode('Allocation failure in GameCardC'),
    3228: ResultCode('Allocation failure in GameCardD'),
    3232: ResultCode('Allocation failure in ImageDirectoryA.'),
    3244: ResultCode('Allocation failure in SDCardA.'),
    3245: ResultCode('Allocation failure in SDCardB.'),
    3246: ResultCode('Allocation failure in SystemSaveDataA.'),
    3247: ResultCode('Allocation failure in RomFsFileSystemA.'),
    3248: ResultCode('Allocation failure in RomFsFileSystemB.'),
    3249: ResultCode('Allocation failure in RomFsFileSystemC.'),
    3256: ResultCode('Allocation failure in FilesystemProxyCoreImplD.'),
    3257: ResultCode('Allocation failure in FilesystemProxyCoreImplE.'),
    3280: ResultCode('Allocation failure in PartitionFileSystemCreatorA.'),
    3281: ResultCode('Allocation failure in RomFileSystemCreatorA.'),
    3288: ResultCode('Allocation failure in StorageOnNcaCreatorA.'),
    3289: ResultCode('Allocation failure in StorageOnNcaCreatorB.'),
    3294: ResultCode('Allocation failure in SystemBuddyHeapA.'),
    3295: ResultCode('Allocation failure in SystemBufferManagerA.'),
    3296: ResultCode('Allocation failure in BlockCacheBufferedStorageA.'),
    3297: ResultCode('Allocation failure in BlockCacheBufferedStorageB.'),
    3304: ResultCode('Allocation failure in IntegrityVerificationStorageA.'),
    3305: ResultCode('Allocation failure in IntegrityVerificationStorageB.'),
    3321: ResultCode('Allocation failure in DirectorySaveDataFileSystem.'),
    3341: ResultCode('Allocation failure in NcaFileSystemDriverI.'),
    3347: ResultCode('Allocation failure in PartitionFileSystemA.'),
    3348: ResultCode('Allocation failure in PartitionFileSystemB.'),
    3349: ResultCode('Allocation failure in PartitionFileSystemC.'),
    3350: ResultCode('Allocation failure in PartitionFileSystemMetaA.'),
    3351: ResultCode('Allocation failure in PartitionFileSystemMetaB.'),
    3355: ResultCode('Allocation failure in SubDirectoryFileSystem.'),
    3359: ResultCode('Out of memory.'),
    3360: ResultCode('Out of memory.'),
    3363: ResultCode('Allocation failure in NcaReaderA.'),
    3365: ResultCode('Allocation failure in RegisterA.'),
    3366: ResultCode('Allocation failure in RegisterB.'),
    3367: ResultCode('Allocation failure in PathNormalizer.'),
    3375: ResultCode('Allocation failure in DbmRomKeyValueStorage.'),
    3377: ResultCode('Allocation failure in RomFsFileSystemE.'),
    3386: ResultCode('Allocation failure in ReadOnlyFileSystemA.'),
    3399: ResultCode('Allocation failure in AesCtrCounterExtendedStorageA.'),
    3400: ResultCode('Allocation failure in AesCtrCounterExtendedStorageB.'),
    3407: ResultCode('Allocation failure in FileSystemInterfaceAdapter.'),
    3411: ResultCode('Allocation failure in BufferedStorageA.'),
    3412: ResultCode('Allocation failure in IntegrityRomFsStorageA.'),
    3420: ResultCode('Allocation failure in New.'),
    3422: ResultCode('Allocation failure in MakeUnique.'),
    3423: ResultCode('Allocation failure in AllocateShared.'),
    3424: ResultCode('Allocation failure in PooledBufferNotEnoughSize.'),
    4000: ResultCode('The data is corrupted.'),
    4002: ResultCode('Unsupported ROM version.'),
    4012: ResultCode('Invalid AesCtrCounterExtendedEntryOffset.'),
    4013: ResultCode('Invalid AesCtrCounterExtendedTableSize.'),
    4014: ResultCode('Invalid AesCtrCounterExtendedGeneration.'),
    4015: ResultCode('Invalid AesCtrCounterExtendedOffset.'),
    4022: ResultCode('Invalid IndirectEntryOffset.'),
    4023: ResultCode('Invalid IndirectEntryStorageIndex.'),
    4024: ResultCode('Invalid IndirectStorageSize.'),
    4025: ResultCode('Invalid IndirectVirtualOffset.'),
    4026: ResultCode('Invalid IndirectPhysicalOffset.'),
    4027: ResultCode('Invalid IndirectStorageIndex.'),
    4032: ResultCode('Invalid BucketTreeSignature.'),
    4033: ResultCode('Invalid BucketTreeEntryCount.'),
    4034: ResultCode('Invalid BucketTreeNodeEntryCount.'),
    4035: ResultCode('Invalid BucketTreeNodeOffset.'),
    4036: ResultCode('Invalid BucketTreeEntryOffset.'),
    4037: ResultCode('Invalid BucketTreeEntrySetOffset.'),
    4038: ResultCode('Invalid BucketTreeNodeIndex.'),
    4039: ResultCode('Invalid BucketTreeVirtualOffset.'),
    4052: ResultCode('ROM NCA filesystem type is invalid.'),
    4053: ResultCode('ROM ACID file size is invalid.'),
    4054: ResultCode('ROM ACID size is invalid.'),
    4055: ResultCode('ROM ACID is invalid.'),
    4056: ResultCode('ROM ACID verification failed.'),
    4057: ResultCode('ROM NCA signature is invalid.'),
    4058: ResultCode('ROM NCA header signature 1 verification failed.'),
    4059: ResultCode('ROM NCA header signature 2 verification failed.'),
    4060: ResultCode('ROM NCA FS header hash verification failed.'),
    4061: ResultCode('ROM NCA key index is invalid.'),
    4062: ResultCode('ROM NCA FS header hash type is invalid.'),
    4063: ResultCode('ROM NCA FS header encryption type is invalid.'),
    4070: ResultCode('ROM data is corrupted.'),
    4072: ResultCode('Invalid ROM hierarchical SHA256 block size.'),
    4073: ResultCode('Invalid ROM hierarchical SHA256 layer count.'),
    4074: ResultCode('ROM hierarchical SHA256 BaseStorage is too large.'),
    4075: ResultCode('ROM hierarchical SHA256 hash verification failed.'),
    4142: ResultCode('Incorrect ROM integrity verification magic.'),
    4143: ResultCode('Invalid ROM0 hash.'),
    4144: ResultCode('ROM non-real data verification failed.'),
    4145: ResultCode('Invalid ROM hierarchical integrity verification layer count.'),
    4151: ResultCode('Cleared ROM real data verification failed.'),
    4152: ResultCode('Uncleared ROM real data verification failed.'),
    4153: ResultCode('Invalid ROM0 hash.'),
    4182: ResultCode('Invalid ROM SHA256 partition hash target.'),
    4183: ResultCode('ROM SHA256 partition hash verification failed.'),
    4184: ResultCode('ROM partition signature verification failed.'),
    4185: ResultCode('ROM SHA256 partition signature verification failed.'),
    4186: ResultCode('Invalid ROM partition entry offset.'),
    4187: ResultCode('Invalid ROM SHA256 partition metadata size.'),
    4202: ResultCode('ROM GPT header verification failed.'),
    4242: ResultCode('ROM host entry corrupted.'),
    4243: ResultCode('ROM host file data corrupted.'),
    4244: ResultCode('ROM host file corrupted.'),
    4245: ResultCode('Invalid ROM host handle.'),
    4262: ResultCode('Invalid ROM allocation table block.'),
    4263: ResultCode('Invalid ROM key value list element index.'),
    4318: ResultCode('Invalid save data filesystem magic (valid magic is SAVE in ASCII).'),
    4508: ResultCode('NcaBaseStorage is out of Range A.'),
    4509: ResultCode('NcaBaseStorage is out of Range B.'),
    4512: ResultCode('Invalid NCA filesystem type.'),
    4513: ResultCode('Invalid ACID file size.'),
    4514: ResultCode('Invalid ACID size.'),
    4515: ResultCode('Invalid ACID.'),
    4516: ResultCode('ACID verification failed.'),
    4517: ResultCode('Invalid NCA signature.'),
    4518: ResultCode('NCA header signature 1 verification failed.'),
    4519: ResultCode('NCA header signature 2 verification failed.'),
    4520: ResultCode('NCA FS header hash verification failed.'),
    4521: ResultCode('Invalid NCA key index.'),
    4522: ResultCode('Invalid NCA FS header hash type.'),
    4523: ResultCode('Invalid NCA FS header encryption type.'),
    4524: ResultCode('Redirection BKTR table size is negative.'),
    4525: ResultCode('Encryption BKTR table size is negative.'),
    4526: ResultCode('Redirection BKTR table end offset is past the Encryption BKTR table start offset.'),
    4527: ResultCode('NCA path used with the wrong program ID.'),
    4528: ResultCode('NCA header value is out of range.'),
    4529: ResultCode('NCA FS header value is out of range.'),
    4530: ResultCode('NCA is corrupted.'),
    4532: ResultCode('Invalid hierarchical SHA256 block size.'),
    4533: ResultCode('Invalid hierarchical SHA256 layer count.'),
    4534: ResultCode('Hierarchical SHA256 base storage is too large.'),
    4535: ResultCode('Hierarchical SHA256 hash verification failed.'),
    4543: ResultCode('Invalid NCA header 1 signature key generation.'),
    4602: ResultCode('Incorrect integrity verification magic.'),
    4603: ResultCode('Invalid zero hash.'),
    4604: ResultCode('Non-real data verification failed.'),
    4605: ResultCode('Invalid hierarchical integrity verification layer count.'),
    4612: ResultCode('Cleared real data verification failed.'),
    4613: ResultCode('Uncleared real data verification failed.'),
    4642: ResultCode('Invalid SHA256 partition hash target.'),
    4643: ResultCode('SHA256 partition hash verification failed.'),
    4644: ResultCode('Partition signature verification failed.'),
    4645: ResultCode('SHA256 partition signature verification failed.'),
    4646: ResultCode('Invalid partition entry offset.'),
    4647: ResultCode('Invalid SHA256 partition metadata size.'),
    4662: ResultCode('GPT header verification failed.'),
    4684: ResultCode('Invalid FAT file number.'),
    4686: ResultCode('Invalid FAT format for BIS USER partition.'),
    4687: ResultCode('Invalid FAT format for BIS SYSTEM partition.'),
    4688: ResultCode('Invalid FAT format for BIS SAFE partition.'),
    4689: ResultCode('Invalid FAT format for BIS PRODINFOF partition.'),
    4702: ResultCode('Host entry is corrupted.'),
    4703: ResultCode('Host file data is corrupted.'),
    4704: ResultCode('Host file is corrupted.'),
    4705: ResultCode('Invalid host handle.'),
    4722: ResultCode('Invalid allocation table block.'),
    4723: ResultCode('Invalid key value list element index.'),
    4743: ResultCode('Corrupted NAX0 header.'),
    4744: ResultCode('Invalid NAX0 magic number.'),
    4781: ResultCode('Game Card logo data is corrupted.'),
    5121: ResultCode('Invalid FAT size.'),
    5122: ResultCode('Invalid FAT BPB (BIOS Parameter Block).'),
    5123: ResultCode('Invalid FAT parameter.'),
    5124: ResultCode('Invalid FAT sector.'),
    5125: ResultCode('Invalid FAT sector.'),
    5126: ResultCode('Invalid FAT sector.'),
    5127: ResultCode('Invalid FAT sector.'),
    5301: ResultCode('Mount point not found.'),
    5315: ResultCode('Unexpected InAesCtrStorageA.'),
    5317: ResultCode('Unexpected InAesXtsStorageA.'),
    5319: ResultCode('Unexpected InFindFileSystemA.'),
    6000: ResultCode('Precondition violation.'),
    6001: ResultCode('Invalid argument.'),
    6003: ResultCode('Path is too long.'),
    6004: ResultCode('Invalid character.'),
    6005: ResultCode('Invalid path format.'),
    6006: ResultCode('Directory is unobtainable.'),
    6007: ResultCode('Not normalized.'),
    6031: ResultCode('The directory is not deletable.'),
    6032: ResultCode('The directory is not renameable.'),
    6033: ResultCode('The path is incompatible.'),
    6034: ResultCode('Rename to other filesystem.'), # 'Attempted to rename to other filesystem.'?
    6061: ResultCode('Invalid offset.'),
    6062: ResultCode('Invalid size.'),
    6063: ResultCode('Argument is nullptr.'),
    6064: ResultCode('Invalid alignment.'),
    6065: ResultCode('Invalid mount name.'),
    6066: ResultCode('Extension size is too large.'),
    6067: ResultCode('Extension size is invalid.'),
    6072: ResultCode('Invalid open mode.'),
    6081: ResultCode('Invalid savedata state.'),
    6082: ResultCode('Invalid savedata space ID.'),
    6201: ResultCode('File extension without open mode AllowAppend.'),
    6202: ResultCode('Reads are not permitted.'),
    6203: ResultCode('Writes are not permitted.'),
    6300: ResultCode('Operation not supported.'),
    6301: ResultCode('A specified filesystem has no MultiCommitTarget when doing a multi-filesystem commit.'),
    6302: ResultCode('Attempted to resize a nn::fs::SubStorage or BufferedStorage that is marked as non-resizable.'),
    6303: ResultCode('Attempted to resize a nn::fs::SubStorage or BufferedStorage when the SubStorage ends before the base storage.'),
    6304: ResultCode('Attempted to call nn::fs::MemoryStorage::SetSize.'),
    6305: ResultCode('Invalid Operation ID in nn::fs::MemoryStorage::OperateRange.'),
    6306: ResultCode('Invalid Operation ID in nn::fs::FileStorage::OperateRange.'),
    6307: ResultCode('Invalid Operation ID in nn::fs::FileHandleStorage::OperateRange.'),
    6308: ResultCode('Invalid Operation ID in nn::fssystem::SwitchStorage::OperateRange.'),
    6309: ResultCode('Invalid Operation ID in nn::fs::detail::StorageServiceObjectAdapter::OperateRange.'),
    6310: ResultCode('Attempted to call nn::fssystem::AesCtrCounterExtendedStorage::Write.'),
    6311: ResultCode('Attempted to call nn::fssystem::AesCtrCounterExtendedStorage::SetSize.'),
    6312: ResultCode('Invalid Operation ID in nn::fssystem::AesCtrCounterExtendedStorage::OperateRange.'),
    6313: ResultCode('Attempted to call nn::fssystem::AesCtrStorageExternal::Write.'),
    6314: ResultCode('Attempted to call nn::fssystem::AesCtrStorageExternal::SetSize.'),
    6315: ResultCode('Attempted to call nn::fssystem::AesCtrStorage::SetSize.'),
    6316: ResultCode('Attempted to call nn::fssystem::save::HierarchicalIntegrityVerificationStorage::SetSize.'),
    6317: ResultCode('Attempted to call nn::fssystem::save::HierarchicalIntegrityVerificationStorage::OperateRange.'),
    6318: ResultCode('Attempted to call nn::fssystem::save::IntegrityVerificationStorage::SetSize.'),
    6319: ResultCode('Attempted to invalidate the cache of a RomFs IVFC storage in nn::fssystem::save::IntegrityVerificationStorage::OperateRange.'),
    6320: ResultCode('Invalid Operation ID in nn::fssystem::save::IntegrityVerificationStorage::OperateRange.'),
    6321: ResultCode('Attempted to call nn::fssystem::save::BlockCacheBufferedStorage::SetSize.'),
    6322: ResultCode('Attempted to invalidate the cache of something other than a savedata IVFC storage in nn::fssystem::save::BlockCacheBufferedStorage::OperateRange.'),
    6323: ResultCode('Invalid Operation ID in nn::fssystem::save::BlockCacheBufferedStorage::OperateRange.'),
    6324: ResultCode('Attempted to call nn::fssystem::IndirectStorage::Write.'),
    6325: ResultCode('Attempted to call nn::fssystem::IndirectStorage::SetSize.'),
    6326: ResultCode('Invalid Operation ID in nn::fssystem::IndirectStorage::OperateRange.'),
    6327: ResultCode('Attempted to call nn::fssystem::SparseStorage::ZeroStorage::Write.'),
    6328: ResultCode('Attempted to call nn::fssystem::SparseStorage::ZeroStorage::SetSize.'),
    6329: ResultCode('Attempted to call nn::fssystem::HierarchicalSha256Storage::SetSize.'),
    6330: ResultCode('Attempted to call nn::fssystem::ReadOnlyBlockCacheStorage::Write.'),
    6331: ResultCode('Attempted to call nn::fssystem::ReadOnlyBlockCacheStorage::SetSize.'),
    6332: ResultCode('Attempted to call nn::fssystem::IntegrityRomFsStorage::SetSize.'),
    6333: ResultCode('Attempted to call nn::fssystem::save::DuplexStorage::SetSize.'),
    6334: ResultCode('Invalid Operation ID in nn::fssystem::save::DuplexStorage::OperateRange.'),
    6335: ResultCode('Attempted to call nn::fssystem::save::HierarchicalDuplexStorage::SetSize.'),
    6336: ResultCode('Attempted to call nn::fssystem::save::RemapStorage::GetSize.'),
    6337: ResultCode('Attempted to call nn::fssystem::save::RemapStorage::SetSize.'),
    6338: ResultCode('Invalid Operation ID in nn::fssystem::save::RemapStorage::OperateRange.'),
    6339: ResultCode('Attempted to call nn::fssystem::save::IntegritySaveDataStorage::SetSize.'),
    6340: ResultCode('Invalid Operation ID in nn::fssystem::save::IntegritySaveDataStorage::OperateRange.'),
    6341: ResultCode('Attempted to call nn::fssystem::save::JournalIntegritySaveDataStorage::SetSize.'),
    6342: ResultCode('Invalid Operation ID in nn::fssystem::save::JournalIntegritySaveDataStorage::OperateRange.'),
    6343: ResultCode('Attempted to call nn::fssystem::save::JournalStorage::GetSize.'),
    6344: ResultCode('Attempted to call nn::fssystem::save::JournalStorage::SetSize.'),
    6345: ResultCode('Invalid Operation ID in nn::fssystem::save::JournalStorage::OperateRange.'),
    6346: ResultCode('Attempted to call nn::fssystem::save::UnionStorage::SetSize.'),
    6347: ResultCode('Attempted to call nn::fssystem::dbm::AllocationTableStorage::SetSize.'),
    6348: ResultCode('Attempted to call nn::fssrv::fscreator::WriteOnlyGameCardStorage::Read.'),
    6349: ResultCode('Attempted to call nn::fssrv::fscreator::WriteOnlyGameCardStorage::SetSize.'),
    6350: ResultCode('Attempted to call nn::fssrv::fscreator::ReadOnlyGameCardStorage::Write.'),
    6351: ResultCode('Attempted to call nn::fssrv::fscreator::ReadOnlyGameCardStorage::SetSize.'),
    6352: ResultCode('Invalid Operation ID in nn::fssrv::fscreator::ReadOnlyGameCardStorage::OperateRange.'),
    6353: ResultCode('Attempted to call SdStorage::SetSize.'),
    6354: ResultCode('Invalid Operation ID in SdStorage::OperateRange.'),
    6355: ResultCode('Invalid Operation ID in nn::fat::FatFile::DoOperateRange.'),
    6356: ResultCode('Invalid Operation ID in nn::fssystem::StorageFile::DoOperateRange.'),
    6357: ResultCode('Attempted to call nn::fssystem::ConcatenationFile::SetSize.'),
    6358: ResultCode('Attempted to call nn::fssystem::ConcatenationFile::OperateRange.'),
    6359: ResultCode('Invalid Query ID in nn::fssystem::ConcatenationFileSystem::DoQueryEntry.'),
    6360: ResultCode('Invalid Operation ID in nn::fssystem::ConcatenationFile::DoOperateRange.'),
    6361: ResultCode('Attempted to call nn::fssystem::ZeroBitmapFile::SetSize.'),
    6362: ResultCode('Invalid Operation ID in nn::fs::detail::FileServiceObjectAdapter::DoOperateRange.'),
    6363: ResultCode('Invalid Operation ID in nn::fssystem::AesXtsFile::DoOperateRange.'),
    6364: ResultCode('Attempted to modify a nn::fs::RomFsFileSystem.'),
    6365: ResultCode('Attempted to call nn::fs::RomFsFileSystem::DoCommitProvisionally.'),
    6366: ResultCode('Attempted to query the space in a nn::fs::RomFsFileSystem.'),
    6367: ResultCode('Attempted to modify a nn::fssystem::RomFsFile.'),
    6368: ResultCode('Invalid Operation ID in nn::fssystem::RomFsFile::DoOperateRange.'),
    6369: ResultCode('Attempted to modify a nn::fs::ReadOnlyFileSystemTemplate.'),
    6370: ResultCode('Attempted to call nn::fs::ReadOnlyFileSystemTemplate::DoCommitProvisionally.'),
    6371: ResultCode('Attempted to query the space in a nn::fs::ReadOnlyFileSystemTemplate.'),
    6372: ResultCode('Attempted to modify a nn::fs::ReadOnlyFileSystemFile.'),
    6373: ResultCode('Invalid Operation ID in nn::fs::ReadOnlyFileSystemFile::DoOperateRange.'),
    6374: ResultCode('UAttempted to modify a nn::fssystem::PartitionFileSystemCore.'),
    6375: ResultCode('Attempted to call nn::fssystem::PartitionFileSystemCore::DoCommitProvisionally.'),
    6376: ResultCode('Attempted to call nn::fssystem::PartitionFileSystemCore::PartitionFile::DoSetSize.'),
    6377: ResultCode('Invalid Operation ID in nn::fssystem::PartitionFileSystemCore::PartitionFile::DoOperateRange.'),
    6378: ResultCode('Invalid Operation ID in nn::fssystem::TmFileSystemFile::DoOperateRange.'),
    6379: ResultCode('Attempted to call unsupported functions in nn::fssrv::fscreator::SaveDataInternalStorageFileSystem, nn::fssrv::detail::SaveDataInternalStorageAccessor::PaddingFile or nn::fssystem::save::detail::SaveDataExtraDataInternalStorageFile.'),
    6382: ResultCode('Attempted to call nn::fssystem::ApplicationTemporaryFileSystem::DoCommitProvisionally.'),
    6383: ResultCode('Attempted to call nn::fssystem::SaveDataFileSystem::DoCommitProvisionally.'),
    6384: ResultCode('Attempted to call nn::fssystem::DirectorySaveDataFileSystem::DoCommitProvisionally.'),
    6385: ResultCode('Attempted to call nn::fssystem::ZeroBitmapHashStorageFile::Write.'),
    6386: ResultCode('Attempted to call nn::fssystem::ZeroBitmapHashStorageFile::SetSize.'),
    6400: ResultCode('Permission denied.'),
    6451: ResultCode('Missing titlekey (required to mount content).'),
    6454: ResultCode('Needs flush.'),
    6455: ResultCode('File not closed.'),
    6456: ResultCode('Directory not closed.'),
    6457: ResultCode('Write-mode file not closed.'),
    6458: ResultCode('Allocator already registered.'),
    6459: ResultCode('Default allocator used.'),
    6461: ResultCode('Allocator alignment violation.'),
    6465: ResultCode('User does not exist.'),
    6602: ResultCode('File not found.'),
    6603: ResultCode('Directory not found.'),
    6705: ResultCode('Buffer allocation failed.'),
    6706: ResultCode('Mapping table full.'),
    6709: ResultCode('Open count limit reached.'),
    6710: ResultCode('Multicommit limit reached.'),
    6811: ResultCode('Map is full.'),
    6902: ResultCode('Not initialized.'),
    6905: ResultCode('Not mounted.'),
    7902: ResultCode('DBM key was not found.'),
    7903: ResultCode('DBM file was not found.'),
    7904: ResultCode('DBM directory was not found.'),
    7906: ResultCode('DBM already exists.'),
    7907: ResultCode('DBM key is full.'),
    7908: ResultCode('DBM directory entry is full.'),
    7909: ResultCode('DBM file entry is full.'),
    7910: ResultCode('RomFs directory has no more child directories/files when iterating.'),
    7911: ResultCode('DBM FindKey finished.'),
    7912: ResultCode('DBM iteration finshed.'),
    7914: ResultCode('Invalid DBM operation.'),
    7915: ResultCode('Invalid DBM path format.'),
    7916: ResultCode('DBM directory name is too long.'),
    7917: ResultCode('DBM filename is too long.')
},
{
        (30, 33): 'Not enough free space.',
        (34, 38): 'Not enough BIS free space.',
        (39, 45): 'Not enough free space.',
        (2000, 2499): 'Failed to access SD card.',
        (2500, 2999): 'Failed to access Game Card.',
        (3200, 3499): 'Allocation failed.',
        (3500, 3999): 'Failed to access eMMC.',
        #(4001, 4200): 'ROM is corrupted.',
        (4001, 4010): 'ROM is corrupted.',
        (4011, 4019): 'AES-CTR CounterExtendedStorage is corrupted.',
        (4021, 4029): 'Indirect storage is corrupted.',
        (4031, 4039): 'Bucket tree is corrupted.',
        (4041, 4050): 'ROM NCA is corrupted.',
        (4051, 4069): 'ROM NCA filesystem is corrupted.',
        (4071, 4079): 'ROM NCA hierarchical SHA256 storage is corrupted.',
        (4141, 4150): 'ROM integrity verification storage is corrupted.',
        (4151, 4159): 'ROM real data verification failed.',
        (4160, 4079): 'ROM integrity verification storage is corrupted.',
        (4181, 4199): 'ROM partition filesystem is corrupted.',
        (4201, 4219): 'ROM built-in storage is corrupted.',
        (4241, 4259): 'ROM host filesystem is corrupted.',
        (4261, 4279): 'ROM database is corrupted.',
        (4280, 4299): 'ROM is corrupted.',
        (4301, 4499): 'Savedata is corrupted.',
        (4501, 4510): 'NCA is corrupted.',
        (4511, 4529): 'NCA filesystem is corrupted.',
        (4531, 4539): 'NCA hierarchical SHA256 storage is corrupted.',
        (4540, 4599): 'NCA is corrupted.',
        (4601, 4610): 'Integrity verification storage is corrupted.',
        (4611, 4619): 'Real data verification failed.',
        (4620, 4639): 'Integrity verification storage is corrupted.',
        (4641, 4659): 'Partition filesystem is corrupted.',
        (4661, 4679): 'Built-in storage is corrupted.',
        (4681, 4699): 'FAT filesystem is corrupted.',
        (4701, 4719): 'Host filesystem is corrupted.',
        (4721, 4739): 'Database is corrupted.',
        (4741, 4759): 'AEX-XTS filesystem is corrupted.',
        (4761, 4769): 'Savedata transfer data is corrupted.',
        (4771, 4779): 'Signed system partition data is corrupted.',
        (4800, 4999): 'The data is corrupted.',
        (5000, 5999): 'Unexpected.',
        (6002, 6029): 'Invalid path.',
        (6030, 6059): 'Invalid path for operation.',
        (6080, 6099): 'Invalid enum value.',
        (6100, 6199): 'Invalid argument.',
        (6200, 6299): 'Invalid operation for open mode.',
        (6300, 6399): 'Unsupported operation.',
        (6400, 6449): 'Permission denied.',
        (6600, 6699): 'Not found.',
        (6700, 6799): 'Out of resources.',
        (6800, 6899): 'Mapping failed.',
        (6900, 6999): 'Bad state.',
        (7901, 7904): 'DBM not found.',
        (7910, 7912): 'DBM find finished.',
})

ncm = Module('ncm', {
    1: ResultCode('Invalid ContentStorageBase.'),
    2: ResultCode('Placeholder already exists.'),
    3: ResultCode('Placeholder not found (issue related to the SD card in use).', 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/22393/kw/2005-0003'),
    4: ResultCode('Content already exists.'),
    5: ResultCode('Content not found.'),
    7: ResultCode('Content meta not found.'),
    8: ResultCode('Allocation failed.'),
    12: ResultCode('Unknown storage.'),
    100: ResultCode('Invalid ContentStorage.'),
    110: ResultCode('Invalid ContentMetaDatabase.'),
    130: ResultCode('Invalid package format.'),
    140: ResultCode('Invalid content hash.'),
    160: ResultCode('Invalid install task state.'),
    170: ResultCode('Invalid placeholder file.'),
    180: ResultCode('Buffer is insufficient.'),
    190: ResultCode('Cannot write to read-only ContentStorage.'),
    200: ResultCode('Not enough install space.'),
    210: ResultCode('System update was not found in package.'),
    220: ResultCode('Content info not found.'),
    237: ResultCode('Delta not found.'),
    240: ResultCode('Invalid content metakey.'),
    251: ResultCode('GameCardContentStorage is not active.'),
    252: ResultCode('BuiltInSystemContentStorage is not active.'),
    253: ResultCode('BuiltInUserContentStorage is not active.'),
    254: ResultCode('SdCardContentStorage is not active.'),
    258: ResultCode('UnknownContentStorage is not active.'),
    261: ResultCode('GameCardContentMetaDatabase is not active.'),
    262: ResultCode('BuiltInSystemMetaDatabase is not active.'),
    263: ResultCode('BuiltInUserMetaDatabase is not active.'),
    264: ResultCode('SdCardContentMetaDatabase is not active.'),
    268: ResultCode('UnknownContentMetaDatabase is not active.'),
    291: ResultCode('Create placeholder was cancelled.'),
    292: ResultCode('Write placeholder was cancelled.'),
    280: ResultCode('Ignorable install ticket failure.'),
    310: ResultCode('ContentStorageBase not found.'),
    330: ResultCode('List partially not committed.'),
    360: ResultCode('Unexpected ContentMeta prepared.'),
    380: ResultCode('Invalid firmware variation.'),
    8182: ResultCode('Invalid offset.')
},
{
    (250, 258): 'Content storage is not active.',
    (260, 268): 'Content meta database is not active.',
    (290, 299): 'Install task was cancelled.',
    (8181, 8191): 'Invalid argument.'
})

os = Module('os', {
    4: ResultCode('Busy.'),
    8: ResultCode('Out of memory.'),
    9: ResultCode('Out of resources.'),
    12: ResultCode('Out of virtual address space.'),
    13: ResultCode('Resource limit reached.'),
    384: ResultCode('File operation failed.'),
    500: ResultCode('Out of handles.'),
    501: ResultCode('Invalid handle.'),
    502: ResultCode('Invalid CurrentMemory state.'),
    503: ResultCode('Invalid TransferMemory state.'),
    504: ResultCode('Invalid TransferMemory size.'),
    505: ResultCode('Out of TransferMemory.'),
    506: ResultCode('Out of address space.')
})

dmnt = Module('dmnt', {
    1: ResultCode('Unknown error.'),
    2: ResultCode('Debugging is disabled.'),

    # atmosphere extension errors
    6500: ResultCode('Not attached.'),
    6501: ResultCode('Buffer is null.'),
    6502: ResultCode('Buffer is invalid.'),
    6503: ResultCode('ID is unknown.'),
    6504: ResultCode('Out of resources.'),
    6505: ResultCode('Cheat is invalid.'),
    6506: ResultCode('Cheat cannot be disabled.'),
    6600: ResultCode('Width is invalid.'),
    6601: ResultCode('Address already exists.'),
    6602: ResultCode('Address not found.'),
    6603: ResultCode('Address is out of resources.'),
    6700: ResultCode('Virtual machine condition depth is invalid.')
},
{
    (6500, 6599): 'Cheat engine error.',
    (6600, 6699): 'Frozen address error.'
})

lr = Module('lr', {
    2: ResultCode('Program not found.'),
    3: ResultCode('Data not found.'),
    4: ResultCode('Unknown storage ID.'),
    5: ResultCode('Access denied.'),
    6: ResultCode('HTML document not found.'),
    7: ResultCode('Add-on Content not found.'),
    8: ResultCode('Control not found.'),
    9: ResultCode('Legal information not found.'),
    10: ResultCode('Debug program not found.'),
    90: ResultCode('Too many registered paths.')
})

loader = Module('loader', {
    1: ResultCode('Argument too long.'),
    2: ResultCode('Too many arguments.'),
    3: ResultCode('Meta is too large.'),
    4: ResultCode('Invalid meta.'),
    5: ResultCode('Invalid NSO.'),
    6: ResultCode('Invalid path.'),
    7: ResultCode('Too many processes.'),
    8: ResultCode('Not pinned.'),
    9: ResultCode('Invalid program ID.'),
    10: ResultCode('Invalid version.'),
    11: ResultCode('Invalid ACID signature.'),
    12: ResultCode('Invalid NCA signature.'),
    51: ResultCode('Insufficient address space.'),
    52: ResultCode('Invalid NRO.'),
    53: ResultCode('Invalid NRR.'),
    54: ResultCode('Invalid signature.'),
    55: ResultCode('Insufficient NRO registrations.'),
    56: ResultCode('Insufficient NRR registrations.'),
    57: ResultCode('NRO already loaded.'),
    81: ResultCode('Unaligned NRR address.'),
    82: ResultCode('Invalid NRR size.'),
    84: ResultCode('NRR not loaded.'),
    85: ResultCode('Not registered (bad NRR address).'),
    86: ResultCode('Invalid session.'),
    87: ResultCode('Invalid process (bad initialization).'),
    100: ResultCode('Unknown capability (unknown ACI0 descriptor).'),
    103: ResultCode('CapabilityKernelFlags is invalid.'),
    104: ResultCode('CapabilitySyscallMask is invalid.'),
    106: ResultCode('CapabilityMapRange is invalid.'),
    107: ResultCode('CapabilityMapPage is invalid.'),
    111: ResultCode('CapabilityInterruptPair is invalid.'),
    113: ResultCode('CapabilityApplicationType is invalid.'),
    114: ResultCode('CapabilityKernelVersion is invalid.'),
    115: ResultCode('CapabilityHandleTable is invalid.'),
    116: ResultCode('CapabilityDebugFlags is invalid.'),
    200: ResultCode('Internal error.')
})

hipc = Module('hipc', {
    1: ResultCode('Unsupported operation.'),
    102: ResultCode('Out of session memory.'),
    (131, 139): ResultCode('Out of sessions.'),
    141: ResultCode('Pointer buffer is too small.'),
    200: ResultCode('Out of domains (session doesn\'t support domains).'),
    301: ResultCode('Session closed.'),
    402: ResultCode('Invalid request size.'),
    403: ResultCode('Unknown command type.'),
    420: ResultCode('Invalid CMIF request.'),
    491: ResultCode('Target is not a domain.'),
    492: ResultCode('Domain object was not found.')
},
{
    (100, 299): 'Out of resources.'
})

pm = Module('pm', {
    1: ResultCode('Process not found.'),
    2: ResultCode('Already started.'),
    3: ResultCode('Not terminated.'),
    4: ResultCode('Debug hook in use.'),
    5: ResultCode('Application running.'),
    6: ResultCode('Invalid size.')
})

ns = Module('ns', {
    90: ResultCode('Canceled.'),
    110: ResultCode('Out of max running tasks.'),
    120: ResultCode('System update is not required.'),
    251: ResultCode('Unexpected storage ID.'),
    270: ResultCode('Card update not set up.'),
    280: ResultCode('Card update not prepared.'),
    290: ResultCode('Card update already set up.'),
    340: ResultCode('IsAnyInternetRequestAccepted with the output from GetClientId returned false.'),
    460: ResultCode('PrepareCardUpdate already requested.'),
    801: ResultCode('SystemDeliveryInfo system_delivery_protocol_version is less than the system setting.'),
    802: ResultCode('SystemDeliveryInfo system_delivery_protocol_version is greater than the system setting.'),
    892: ResultCode('Unknown state: reference count is zero.'),
    931: ResultCode('Invalid SystemDeliveryInfo HMAC/invalid Meta ID.'),
    2101: ResultCode('Inserted region-locked Tencent-Nintendo (Chinese) game cartridge into a non-Chinese console.', 'https://nintendoswitch.com.cn/support/')
})

sm = Module('sm', {
    1: ResultCode('Out of processes.'),
    2: ResultCode('Invalid client (not initialized).'),
    3: ResultCode('Out of sessions.'),
    4: ResultCode('Already registered.'),
    5: ResultCode('Out of services.'),
    6: ResultCode('Invalid service name.'),
    7: ResultCode('Not registered.'),
    8: ResultCode('Not allowed (permission denied).'),
    9: ResultCode('Access control is too large.'),

    1000: ResultCode('Should forward to session.'),
    1100: ResultCode('Process is not associated.')
},
{
    (1000, 2000): 'Atmosphere man-in-the-middle (MITM) extension result.'
})

ro = Module('ro', {
    2: ResultCode('Out of address space.'),
    3: ResultCode('NRO already loaded.'),
    4: ResultCode('Invalid NRO.'),
    6: ResultCode('Invalid NRR.'),
    7: ResultCode('Too many NROs.'),
    8: ResultCode('Too many NRRs.'),
    9: ResultCode('Not authorized (bad NRO hash or NRR signature).'),
    10: ResultCode('Invalid NRR type.'),
    1023: ResultCode('Internal error.'),
    1025: ResultCode('Invalid address.'),
    1026: ResultCode('Invalid size.'),
    1028: ResultCode('NRO not loaded.'),
    1029: ResultCode('NRO not registered.'),
    1030: ResultCode('Invalid session (already initialized).'),
    1031: ResultCode('Invalid process (not initialized).')
})

settings = Module('settings', {
    11: ResultCode('Settings item not found.'),
    101: ResultCode('Settings item key allocation failed.'),
    102: ResultCode('Settings item value allocation failed.'),
    201: ResultCode('Settings name is null.'),
    202: ResultCode('Settings item key is null.'),
    203: ResultCode('Settings item value is null.'),
    204: ResultCode('Settings item key buffer is null.'),
    205: ResultCode('Settings item value buffer is null.'),
    221: ResultCode('Settings name is empty.'),
    222: ResultCode('Settings item key is empty.'),
    241: ResultCode('Settings group name is too long.'),
    242: ResultCode('Settings item key is too long.'),
    261: ResultCode('Settings group name has invalid format.'),
    262: ResultCode('Settings item key has invalid format.'),
    263: ResultCode('Settings item value has invalid format.'),
    621: ResultCode('Language code.'),
    625: ResultCode('Language out of range.'),
    631: ResultCode('Network.'),
    651: ResultCode('Bluetooth device.'),
    652: ResultCode('Bluetooth device setting output count.'),
    653: ResultCode('Bluetooth enable flag.'),
    654: ResultCode('Bluetooth AFH enable flag.'),
    655: ResultCode('Bluetooth boost enable flag.'),
    656: ResultCode('BLE pairing.'),
    657: ResultCode('BLE pairing settings entry count.'),
    661: ResultCode('External steady clock source ID.'),
    662: ResultCode('User system clock context.'),
    663: ResultCode('Network system clock context.'),
    664: ResultCode('User system clock automatic correction enabled flag.'),
    665: ResultCode('Shutdown RTC value.'),
    666: ResultCode('External steady clock internal offset.'),
    671: ResultCode('Account settings.'),
    681: ResultCode('Audio volume.'),
    683: ResultCode('ForceMuteOnHeadphoneRemoved.'),
    684: ResultCode('Headphone volume warning.'),
    687: ResultCode('Invalid audio output mode.'),
    688: ResultCode('Headphone volume update flag.'),
    691: ResultCode('Console information upload flag.'),
    701: ResultCode('Automatic application download flag.'),
    702: ResultCode('Notification settings.'),
    703: ResultCode('Account notification settings entry count.'),
    704: ResultCode('Account notification settings.'),
    711: ResultCode('Vibration master volume.'),
    712: ResultCode('NX controller settings.'),
    713: ResultCode('NX controller settings entry count.'),
    714: ResultCode('USB full key enable flag.'),
    721: ResultCode('TV settings.'),
    722: ResultCode('EDID.'),
    731: ResultCode('Data deletion settings.'),
    741: ResultCode('Initial system applet program ID.'),
    742: ResultCode('Overlay disp program ID.'),
    743: ResultCode('IsInRepairProcess.'),
    744: ResultCode('RequresRunRepairTimeReviser.'),
    751: ResultCode('Device timezone location name.'),
    761: ResultCode('Primary album storage.'),
    771: ResultCode('USB 3.0 enable flag.'),
    772: ResultCode('USB Type-C power source circuit version.'),
    781: ResultCode('Battery lot.'),
    791: ResultCode('Serial number.'),
    801: ResultCode('Lock screen flag.'),
    803: ResultCode('Color set ID.'),
    804: ResultCode('Quest flag.'),
    805: ResultCode('Wireless certification file size.'),
    806: ResultCode('Wireless certification file.'),
    807: ResultCode('Initial launch settings.'),
    808: ResultCode('Device nickname.'),
    809: ResultCode('Battery percentage flag.'),
    810: ResultCode('Applet launch flags.'),
    1012: ResultCode('Wireless LAN enable flag.'),
    1021: ResultCode('Product model.'),
    1031: ResultCode('NFC enable flag.'),
    1041: ResultCode('ECI device certificate.'),
    1042: ResultCode('E-Ticket device certificate.'),
    1051: ResultCode('Sleep settings.'),
    1061: ResultCode('EULA version.'),
    1062: ResultCode('EULA version entry count.'),
    1071: ResultCode('LDN channel.'),
    1081: ResultCode('SSL key.'),
    1082: ResultCode('SSL certificate.'),
    1091: ResultCode('Telemetry flags.'),
    1101: ResultCode('Gamecard key.'),
    1102: ResultCode('Gamecard certificate.'),
    1111: ResultCode('PTM battery lot.'),
    1112: ResultCode('PTM fuel gauge parameter.'),
    1121: ResultCode('ECI device key.'),
    1122: ResultCode('E-Ticket device key.'),
    1131: ResultCode('Speaker parameter.'),
    1141: ResultCode('Firmware version.'),
    1142: ResultCode('Firmware version digest.'),
    1143: ResultCode('Rebootless system update version.'),
    1151: ResultCode('Mii author ID.'),
    1161: ResultCode('Fatal flags.'),
    1171: ResultCode('Auto update enable flag.'),
    1181: ResultCode('External RTC reset flag.'),
    1191: ResultCode('Push notification activity mode.'),
    1201: ResultCode('Service discovery control setting.'),
    1211: ResultCode('Error report share permission.'),
    1221: ResultCode('LCD vendor ID.'),
    1231: ResultCode('SixAxis sensor acceleration bias.'),
    1232: ResultCode('SixAxis sensor angular velocity bias.'),
    1233: ResultCode('SixAxis sensor acceleration gain.'),
    1234: ResultCode('SixAxis sensor angular velocity gain.'),
    1235: ResultCode('SixAxis sensor angular velocity time bias.'),
    1236: ResultCode('SixAxis sensor angular acceleration.'),
    1241: ResultCode('Keyboard layout.'),
    1245: ResultCode('Invalid keyboard layout.'),
    1251: ResultCode('Web inspector flag.'),
    1252: ResultCode('Allowed SSL hosts.'),
    1253: ResultCode('Allowed SSL hosts entry count.'),
    1254: ResultCode('FS mount point.'),
    1271: ResultCode('Amiibo key.'),
    1272: ResultCode('Amiibo ECQV certificate.'),
    1273: ResultCode('Amiibo ECDSA certificate.'),
    1274: ResultCode('Amiibo ECQV BLS key.'),
    1275: ResultCode('Amiibo ECQV BLS certificate.'),
    1276: ResultCode('Amiibo ECQV BLS root certificate.')
},
{
    (100, 149): 'Internal error.',
    (200, 399): 'Invalid argument.',
    (621, 1276): 'Setting buffer is null.',
})

erpt = Module('erpt', {
    1: ResultCode('Not initialized.'),
    2: ResultCode('Already initialized.'),
    3: ResultCode('Out of array space.'),
    4: ResultCode('Out of field space.'),
    5: ResultCode('Out of memory.'),
    7: ResultCode('Invalid argument.'),
    8: ResultCode('Not found.'),
    9: ResultCode('Field category mismatch.'),
    10: ResultCode('Field type mismatch.'),
    11: ResultCode('Already exists.'),
    12: ResultCode('Journal is corrupted.'),
    13: ResultCode('Category not found.'),
    14: ResultCode('Required context is missing.'),
    15: ResultCode('Required field is missing.'),
    16: ResultCode('Formatter error.'),
    17: ResultCode('Invalid power state.'),
    18: ResultCode('Array field is too large.'),
    19: ResultCode('Already owned.')
})

calibration = Module('calibration', {
    101: ResultCode('Calibration data CRC error.'),
})

dbg = Module('dbg', {
    1: ResultCode('Cannot debug.'),
    2: ResultCode('Already attached.'),
    3: ResultCode('Cancelled.')
})

userland_assert = Module('userland (assert)', {
    0: ResultCode('Undefined instruction.'),
    1: ResultCode('Application aborted (usually svcBreak).'),
    2: ResultCode('System module aborted.'),
    3: ResultCode('Unaligned userland PC.'),
    8: ResultCode('Attempted to call an SVC outside of the whitelist.')
})

fatal = Module('fatal', {
    1: ResultCode('Allocation failed.'),
    2: ResultCode('Graphics buffer is null.'),
    3: ResultCode('Already thrown.'),
    4: ResultCode('Too many events.'),
    5: ResultCode('In repair without volume held.'),
    6: ResultCode('In repair without time reviser cartridge.')
})

i2c = Module('i2c', {
    1: ResultCode('No ACK.'),
    2: ResultCode('Bus is busy.'),
    3: ResultCode('Command list is full.'),
    4: ResultCode('Timed out.'),
    5: ResultCode('Unknown device.')
})

kvdb = Module('kvdb', {
    1: ResultCode('Out of key resources.'),
    2: ResultCode('Key not found.'),
    4: ResultCode('Allocation failed.'),
    5: ResultCode('Invalid key value.'),
    6: ResultCode('Buffer insufficient.'),
    8: ResultCode('Invalid filesystem state.'),
    9: ResultCode('Not created.')
})

updater = Module('updater', {
    2: ResultCode('Boot image package not found.'),
    3: ResultCode('Invalid boot image package.'),
    4: ResultCode('Work buffer is too small.'),
    5: ResultCode('Work buffer is not aligned.'),
    6: ResultCode('Needs repair boot images.')
})

vi = Module('vi', {
    1: ResultCode('Operation failed.'),
    6: ResultCode('Not supported.'),
    7: ResultCode('Not found.')
})

nfp = Module('nfp', {
    64: ResultCode('Device not found.'),
    96: ResultCode('Needs restart.'),
    128: ResultCode('Area needs to be created.'),
    152: ResultCode('Access ID mismatch.'),
    168: ResultCode('Area already created.')
})

psc = Module('psc', {
    2: ResultCode('Already initialized.'),
    3: ResultCode('Not initialized.')
})

time = Module('time', {
    0: ResultCode('Not initialized.'),
    1: ResultCode('Permission denied.'),
    102: ResultCode('Time not set (clock source ID mismatch).'),
    200: ResultCode('Not comparable.'),
    201: ResultCode('Signed over/under-flow.'),
    801: ResultCode('Memory allocation failure.'),
    901: ResultCode('Invalid pointer.'),
    902: ResultCode('Value out of range.'),
    903: ResultCode('TimeZoneRule conversion failed.'),
    989: ResultCode('TimeZone location name not found.'),
    990: ResultCode('Unimplemented.')
},
{
    (900, 919): 'Invalid argument.'
})

bcat = Module('bcat', {
    1: ResultCode('Invalid argument.'),
    2: ResultCode('Object not found.'),
    3: ResultCode('Object locked (in use).'),
    4: ResultCode('Target already mounted.'),
    5: ResultCode('Target not mounted.'),
    6: ResultCode('Object already opened.'),
    7: ResultCode('Object not opened.'),
    8: ResultCode('IsAnyInternetRequestAccepted with the output from GetClientId returned false.'),
    80: ResultCode('Passphrase not found.'),
    81: ResultCode('Data verification failed.'),
    90: ResultCode('Invalid API call.'),
    98: ResultCode('Invalid operation.')
})

ssl = Module('ssl', {
    11: ResultCode('Returned during various NSS SEC, NSPR and NSS SSL errors.', 'https://switchbrew.org/wiki/Error_codes'),
    13: ResultCode('Unrecognized error.'),
    102: ResultCode('Out of memory or table full (NSS SEC error -8173 or NSPR errors -6000, -5974, -5971).'),
    116: ResultCode('NSPR error -5999 (PR_BAD_DESCRIPTOR_ERROR).'),
    204: ResultCode('NSPR error -5998 (PR_WOULD_BLOCK_ERROR).'),
    205: ResultCode('NSPR error -5990 (PR_IO_TIMEOUT_ERROR).'),
    206: ResultCode('NSPR error -5935 (PR_OPERATION_ABORTED_ERROR)..'),
    208: ResultCode('NSPR error -5978 (PR_NOT_CONNECTED_ERROR).'),
    209: ResultCode('NSPR error -5961 (PR_CONNECT_RESET_ERROR).'),
    210: ResultCode('NSPR error -5928 (PR_CONNECT_ABORTED_ERROR).'),
    211: ResultCode('NSPR error -5929 (PR_SOCKET_SHUTDOWN_ERROR).'),
    212: ResultCode('NSPR error -5930 (PR_NETWORK_DOWN_ERROR).'),
    215: ResultCode('ClientPki/InternalPki was already previously imported/registered.'),
    218: ResultCode('Maximum number of ServerPki objects were already imported.'),
    301: ResultCode('NSS SSL error -12276 (SSL_ERROR_BAD_CERT_DOMAIN).'),
    302: ResultCode('NSS SSL error -12285 (SSL_ERROR_NO_CERTIFICATE).'),
    303: ResultCode('NSS SEC errors: -8181 (SEC_ERROR_EXPIRED_CERTIFICATE), -8162 (SEC_ERROR_EXPIRED_ISSUER_CERTIFICATE).'),
    304: ResultCode('NSS SEC error -8180 (SEC_ERROR_REVOKED_CERTIFICATE).'),
    305: ResultCode('NSS SEC error -8183 (SEC_ERROR_BAD_DER).'),
    306: ResultCode('NSS SEC errors: -8102 (SEC_ERROR_INADEQUATE_KEY_USAGE), -8101 (SEC_ERROR_INADEQUATE_CERT_TYPE).'),
    307: ResultCode('NSS SEC errors: -8185 (SEC_ERROR_INVALID_AVA), -8182 (SEC_ERROR_BAD_SIGNATURE), -8158 (SEC_ERROR_EXTENSION_VALUE_INVALID), -8156 (SEC_ERROR_CA_CERT_INVALID), -8151 (SEC_ERROR_UNKNOWN_CRITICAL_EXTENSION), -8080 (SEC_ERROR_CERT_NOT_IN_NAME_SPACE).'),
    308: ResultCode('NSS SEC errors: -8179 (SEC_ERROR_UNKNOWN_ISSUER), -8172 (SEC_ERROR_UNTRUSTED_ISSUER), -8014 (SEC_ERROR_APPLICATION_CALLBACK_ERROR).'),
    309: ResultCode('NSS SEC error -8171 (SEC_ERROR_UNTRUSTED_CERT).'),
    310: ResultCode('NSS SSL errors: -12233 (SSL_ERROR_RX_UNKNOWN_RECORD_TYPE), -12232 (SSL_ERROR_RX_UNKNOWN_HANDSHAKE), -12231 (SSL_ERROR_RX_UNKNOWN_ALERT). This is also returned by ImportClientPki when import fails.'),
    311: ResultCode('NSS SSL errors: One of various malformed request errors. See Switchbrew for the complete list.'),
    312: ResultCode('NSS SEC errors: One of various unexpected request errors. See Switchbrew for the complete list.'),
    313: ResultCode(' NSS SSL errors: -12237 (SSL_ERROR_RX_UNEXPECTED_CHANGE_CIPHER), -12236 (SSL_ERROR_RX_UNEXPECTED_ALERT), -12235 (SSL_ERROR_RX_UNEXPECTED_HANDSHAKE), -12234 (SSL_ERROR_RX_UNEXPECTED_APPLICATION_DATA).'),
    314: ResultCode('NSS SSL error -12263 (SSL_ERROR_RX_RECORD_TOO_LONG).'),
    315: ResultCode('NSS SSL error -12165 (SSL_ERROR_RX_UNEXPECTED_HELLO_VERIFY_REQUEST).'),
    316: ResultCode('NSS SSL error -12163 (SSL_ERROR_RX_UNEXPECTED_CERT_STATUS).'),
    317: ResultCode('NSS SSL error -12160 (SSL_ERROR_INCORRECT_SIGNATURE_ALGORITHM).'),
    318: ResultCode('NSS SSL errors: -12173 (SSL_ERROR_WEAK_SERVER_EPHEMERAL_DH_KEY), -12156 (SSL_ERROR_WEAK_SERVER_CERT_KEY).'),
    319: ResultCode('NSS SSL error -12273 (SSL_ERROR_BAD_MAC_READ).'),
    321: ResultCode('NSS SSL errors: -12215 (SSL_ERROR_MD5_DIGEST_FAILURE), -12214 (SSL_ERROR_SHA_DIGEST_FAILURE), -12161 (SSL_ERROR_DIGEST_FAILURE).'),
    322: ResultCode('NSS SSL error -12213 (SSL_ERROR_MAC_COMPUTATION_FAILURE).'),
    324: ResultCode('NSS SEC error -8157 (SEC_ERROR_EXTENSION_NOT_FOUND).'),
    325: ResultCode('NSS SEC error -8049 (SEC_ERROR_UNRECOGNIZED_OID).'),
    326: ResultCode('NSS SEC error -8032 (SEC_ERROR_POLICY_VALIDATION_FAILED).'),
    330: ResultCode('NSS SSL error -12177 (SSL_ERROR_DECOMPRESSION_FAILURE).'),
    1501: ResultCode('NSS SSL error -12230 (SSL_ERROR_CLOSE_NOTIFY_ALERT).'),
    1502: ResultCode('NSS SSL error -12229 (SSL_ERROR_HANDSHAKE_UNEXPECTED_ALERT).'),
    1503: ResultCode('NSS SSL error -12272 (SSL_ERROR_BAD_MAC_ALERT).'),
    1504: ResultCode('NSS SSL error -12197 (SSL_ERROR_DECRYPTION_FAILED_ALERT).'),
    1505: ResultCode('NSS SSL error -12196 (SSL_ERROR_RECORD_OVERFLOW_ALERT).'),
    1506: ResultCode('NSS SSL error -12228 (SSL_ERROR_DECOMPRESSION_FAILURE_ALERT).'),
    1507: ResultCode('NSS SSL error -12227 (SSL_ERROR_HANDSHAKE_FAILURE_ALERT).'),
    1509: ResultCode('NSS SSL error -12271 (SSL_ERROR_BAD_CERT_ALERT).'),
    1510: ResultCode('NSS SSL error -12225 (SSL_ERROR_UNSUPPORTED_CERT_ALERT).'),
    1511: ResultCode('NSS SSL error -12270 (SSL_ERROR_REVOKED_CERT_ALERT).'),
    1512: ResultCode('NSS SSL error -12269 (SSL_ERROR_EXPIRED_CERT_ALERT).'),
    1513: ResultCode('NSS SSL error -12224 (SSL_ERROR_CERTIFICATE_UNKNOWN_ALERT).'),
    1514: ResultCode('NSS SSL error -12226 (SSL_ERROR_ILLEGAL_PARAMETER_ALERT).'),
    1515: ResultCode('NSS SSL error -12195 (SSL_ERROR_UNKNOWN_CA_ALERT).'),
    1516: ResultCode('NSS SSL error -12194 (SSL_ERROR_ACCESS_DENIED_ALERT).'),
    1517: ResultCode('NSS SSL error -12193 (SSL_ERROR_DECODE_ERROR_ALERT).'),
    1518: ResultCode('NSS SSL error -12192 (SSL_ERROR_DECRYPT_ERROR_ALERT).'),
    1519: ResultCode('NSS SSL error -12191 (SSL_ERROR_EXPORT_RESTRICTION_ALERT).'),
    1520: ResultCode('NSS SSL error -12190 (SSL_ERROR_PROTOCOL_VERSION_ALERT).'),
    1521: ResultCode('NSS SSL error -12189 (SSL_ERROR_INSUFFICIENT_SECURITY_ALERT).'),
    1522: ResultCode('NSS SSL error -12188 (SSL_ERROR_INTERNAL_ERROR_ALERT).'),
    1523: ResultCode('NSS SSL error -12157 (SSL_ERROR_INAPPROPRIATE_FALLBACK_ALERT).'),
    1524: ResultCode('NSS SSL error -12187 (SSL_ERROR_USER_CANCELED_ALERT).'),
    1525: ResultCode('NSS SSL error -12186 (SSL_ERROR_NO_RENEGOTIATION_ALERT).'),
    1526: ResultCode('NSS SSL error -12184 (SSL_ERROR_UNSUPPORTED_EXTENSION_ALERT).'),
    1527: ResultCode('NSS SSL error -12183 (SSL_ERROR_CERTIFICATE_UNOBTAINABLE_ALERT).'),
    1528: ResultCode('NSS SSL error -12182 (SSL_ERROR_UNRECOGNIZED_NAME_ALERT).'),
    1529: ResultCode('NSS SSL error -12181 (SSL_ERROR_BAD_CERT_STATUS_RESPONSE_ALERT).'),
    1530: ResultCode('NSS SSL error -12180 (SSL_ERROR_BAD_CERT_HASH_VALUE_ALERT).'),
    5001: ResultCode('NSS SSL error -12155 (SSL_ERROR_RX_SHORT_DTLS_READ).'),
    5007: ResultCode('Out-of-bounds error during error conversion.')
})

creport = Module('userland assert/crash', {
    0: ResultCode('Undefined instruction.'),
    1: ResultCode('Instruction abort.'),
    2: ResultCode('Data abort.'),
    3: ResultCode('Alignment fault.'),
    4: ResultCode('Debugger attached.'),
    5: ResultCode('Breakpoint.'),
    6: ResultCode('User break.'),
    7: ResultCode('Debugger break.'),
    8: ResultCode('Undefined system call.'),
    9: ResultCode('Memory system error.'),
    99: ResultCode('Report is incomplete.')
})

pgl = Module('pgl', {
    2: ResultCode('Not available.'),
    3: ResultCode('Application not running.'),
    4: ResultCode('Buffer is not enough.'),
    5: ResultCode('Application content record was not found.'),
    6: ResultCode('Content meta was not found.')
})

nim = Module('nim', {
    10: ResultCode('Already initialized.'),
    30: ResultCode('Task not found.'),
    40: ResultCode('Memory allocation failed (due to bad input?).'),
    70: ResultCode('HTTP connection canceled.'),
    330: ResultCode('ContentMetaType does not match SystemUpdate.'),
    5001: ResultCode('A socket error occurred (ENETDOWN, ECONNRESET, EHOSTDOWN, EHOSTUNREACH, or EPIPE). Also occurs when the received size doesn\'t match the expected size (recvfrom() ret with meta_size data receiving).'),
    5010: ResultCode('Socket was shutdown due to the async operation being cancelled.'),
    5020: ResultCode('Too many internal input entries with nim command 42, or an unrecognized socket error occurred.'),
    5100: ResultCode('Connection time-out.'),
    5410: ResultCode('Invalid ID.'),
    5420: ResultCode('Invalid magicnum. Can also be caused by the connection being closed by the peer, since non-negative return values from recv() are ignored in this case.'),
    5430: ResultCode('Invalid data_size.'),
    5440: ResultCode('The input ContentMetaKey doesn\'t match the ContentMetaKey in state.'),
    5450: ResultCode('Invalid meta_size.'),
    7001: ResultCode('Invalid HTTP response code (>=600).'),
    7002: ResultCode('Invalid HTTP client response code (4xx).'),
    7003: ResultCode('Invalid HTTP server response code (5xx).'),
    7004: ResultCode('Invalid HTTP redirect response code (3xx).'),
    (7300, 7308): ResultCode('HTTP response code 300-308.'),
    (7400, 7417): ResultCode('HTTP response code 400-417.'),
    (7500, 7509): ResultCode('HTTP response code 500-509.'),
    7800: ResultCode('Unknown/invalid libcurl error.'),
    (8001, 8096): ResultCode('libcurl error 1-96. Some errors map to the 7800 result code range instead, however.')
})

dauth = Module('dauth', {
    4008: ResultCode('Console is permanently banned by Nintendo.', 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/42061/kw/2181-4008', is_ban=True)
})

web_applet = Module('web applet', {
    1006: ResultCode('This error code indicates an issue with the DNS used or that the connection timed out.', 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/25859/p/897'),
    1028: ResultCode('This error code generally indicates that your connection to the Nintendo eShop has timed out.', 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/22503/p/897'),
    2750: ResultCode('MP4 parsing failed.'),
    5001: ResultCode('This error code indicates an error occurred when connecting to the service, likely the result of the network environment.',  'https://en-americas-support.nintendo.com/app/answers/detail/a_id/22392/p/897'),
})

friends = Module('friends', {
    6: ResultCode('IsAnyInternetRequestAccepted with the output from GetClientId returned false.'),
})

spl = Module('spl', {
    1: ResultCode('Secure monitor: function is not implemented.'),
    2: ResultCode('Secure monitor: invalid argument.'),
    3: ResultCode('Secure monitor is busy.'),
    4: ResultCode('Secure monitor: function is not an async operation.'),
    5: ResultCode('Secure monitor: invalid async operation.'),
    6: ResultCode('Secure monitor: not permitted.'),
    7: ResultCode('Secure monitor: not initialized.'),
    100: ResultCode('Invalid size.'),
    101: ResultCode('Unknown secure monitor error.'),
    102: ResultCode('Decryption failed.'),
    104: ResultCode('Out of keyslots.'),
    105: ResultCode('Invalid keyslot.'),
    106: ResultCode('Boot reason was aleady set.'),
    107: ResultCode('Boot reason was not set.'),
    108: ResultCode('Invalid argument.')
},
{
    (0, 99): 'Secure monitor error.'
})

account = Module('account', {
    59: ResultCode('IsAnyInternetRequestAccepted with the output from GetClientId returned false.'),
    3000: ResultCode('System update is required.', 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/27166/'),
    4007: ResultCode('Console is permanently banned.', 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/28046/', is_ban=True),
    4025: ResultCode('Game Card is banned. If you have a legitimate cartridge and this happened to you, contact Nintendo.', is_ban=True),
    4027: ResultCode('Console (and Nintendo Account) are temporarily banned from a game.', is_ban=True),
    4508: ResultCode('Console is permanently banned.', 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/28046/', is_ban=True),
    4517: ResultCode('Console is permanently banned.', 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/43652/', is_ban=True),
    4609: ResultCode('The online service is no longer available.', 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/46482/'),
    4621: ResultCode('Tencent-Nintendo (Chinese) consoles cannot use online features in foreign games.' 'https://nintendoswitch.com.cn/support/'),
    5111: ResultCode('Complete account ban.', is_ban=True)
})

sf = Module('sf', {
    1: ResultCode('Not supported.'),
    3: ResultCode('Precondition violation.'),
    202: ResultCode('Invalid header size.'),
    211: ResultCode('Invalid in header.'),
    212: ResultCode('Invalid out header.'),
    221: ResultCode('Unknown command ID.'),
    232: ResultCode('Invalid out raw size.'),
    235: ResultCode('Invalid number of in objects.'),
    236: ResultCode('Invalid number of out objects.'),
    239: ResultCode('Invalid in object.'),
    261: ResultCode('Target not found.'),
    301: ResultCode('Out of domain entries.'),
    800: ResultCode('Request invalidated.'),
    802: ResultCode('Request invalidated by user.'),
    812: ResultCode('Request deferred by user.'),
},
{
    (800, 809): 'Request invalidated.',
    (810, 819): 'Request deferred.',
    (820, 899): 'Request context changed.'
})

capsrv = Module('capsrv (capture)', {
    3: ResultCode('Album work memory error.'),
    7: ResultCode('Album is already opened.'),
    8: ResultCode('Album is out of range.'),
    11: ResultCode('The application ID is invalid.'),
    12: ResultCode('The timestamp is invalid.'),
    13: ResultCode('The storage is invalid.'),
    14: ResultCode('The filecontents is invalid.'),
    21: ResultCode('Album is not mounted.'),
    22: ResultCode('Album is full.'),
    23: ResultCode('File not found.'),
    24: ResultCode('The file data is invalid.'),
    25: ResultCode('The file count limit has been reached.'),
    26: ResultCode('The file has no thumbnail.'),
    30: ResultCode('The read buffer is too small.'),
    96: ResultCode('The destination is corrupted.'),
    820: ResultCode('Control resource limit reached.'),
    822: ResultCode('Control is not opened.'),
    1023: ResultCode('Not supported.'),
    1210: ResultCode('Internal JPEG encoder error.'),
    1212: ResultCode('Internal JPEG work memory shortage.'),
    1301: ResultCode('The file data was empty.'),
    1302: ResultCode('EXIF extraction failed.'),
    1303: ResultCode('EXIF data analysis failed.'),
    1304: ResultCode('Datetime extraction failed.'),
    1305: ResultCode('Invalid datetime length.'),
    1306: ResultCode('Inconsistent datatime.'),
    1307: ResultCode('Make note extraction failed.'),
    1308: ResultCode('Inconsistent application ID.'),
    1309: ResultCode('Inconsistent signature.'),
    1310: ResultCode('Unsupported orientation.'),
    1311: ResultCode('Invalid data dimension.'),
    1312: ResultCode('Inconsistent orientation.'),
    1401: ResultCode('File count limit has been reached.'),
    1501: ResultCode('EXIF extraction failed.'),
    1502: ResultCode('Maker note extraction failed'),
    1701: ResultCode('Album session limit reached.'),
    1901: ResultCode('File count limit reached.'),
    1902: ResultCode('Error when creating file.'),
    1903: ResultCode('File creation retry limit reached.'),
    1904: ResultCode('Error opening file.'),
    1905: ResultCode('Error retrieving the file size.'),
    1906: ResultCode('Error setting the file size.'),
    1907: ResultCode('Error when reading the file.'),
    1908: ResultCode('Error when writing the file.')
},
{
    (10, 19): 'Album: invalid file ID.',
    (90, 99): 'Album: filesystem error.',
    (800, 899): 'Control error.',
    #(1024, 2047): 'Internal error.',
    (1200,1299): 'Internal JPEG encoder error.',
    (1300, 1399): 'Internal file data verification error.',
    (1400, 1499): 'Internal album limitation error.',
    (1500, 1599): 'Internal signature error.',
    (1700, 1799): 'Internal album session error.',
    (1900, 1999): 'Internal album temporary file error.'

})

mii = Module('mii', {
    1: ResultCode('Invalid argument.'),
    4: ResultCode('Entry not found.'),
    67: ResultCode('Invalid database signature value (should be "NFDB").'),
    69: ResultCode('Invalid database entry count.'),
    204: ResultCode('Development/debug-only behavior.')
})

am = Module('am', {
    2: ResultCode('IStorage not available.'),
    3: ResultCode('No messages.'),
    35: ResultCode('Error while launching applet.'),
    37: ResultCode('Program ID not found. This usually happens when applet launch fails.'),
    500: ResultCode('Invalid input.'),
    502: ResultCode('IStorage is already opened.'),
    503: ResultCode('IStorage read/write out of bounds.'),
    506: ResultCode('Invalid parameters.'),
    511: ResultCode('IStorage opened as wrong type (e.g. data opened as TransferMemory, or TransferMemory opened as data.'),
    518: ResultCode('Null object.'),
    600: ResultCode('Failed to allocate memory for IStorage.'),
    712: ResultCode('Thread stack pool exhausted.'),
    974: ResultCode('DebugMode not enabled.'),
    980: ResultCode('am.debug!dev_function setting needs to be set (DebugMode not enabled).'),
    998: ResultCode('Not implemented.'),
})

prepo = Module('prepo', {
    102: ResultCode('Transmission not agreed.'),
    105: ResultCode('Network unavailable.'),
    1005: ResultCode('Couldn\'t resolve proxy.'),
    1006: ResultCode('Couldn\'t resolve host.'),
    1007: ResultCode('Couldn\'t connect.'),
    1023: ResultCode('Write error.'),
    1026: ResultCode('Read error.'),
    1027: ResultCode('Out of memory.'),
    1028: ResultCode('Operation timed out.'),
    1035: ResultCode('SSL connection error.'),
    1051: ResultCode('Peer failed verification.'),
    1052: ResultCode('Got nothing.'),
    1055: ResultCode('Send error.'),
    1056: ResultCode('Recv error.'),
    1058: ResultCode('SSL cert problem.'),
    1059: ResultCode('SSL cipher.'),
    1060: ResultCode('SSL CA cert.'),
    2400: ResultCode('Status 400.'),
    2401: ResultCode('Status 401.'),
    2403: ResultCode('Status 403.'),
    2500: ResultCode('Status 500.'),
    2503: ResultCode('Status 503.'),
    2504: ResultCode('Status 504.'),
},
{
    (1005, 1060): 'HTTP error.',
    (2400, 2504): 'Server error.'
})

pcv = Module('pcv', {
    2: ResultCode('Invalid DVFS table ID.'),
    3: ResultCode('DVFS table ID for debug only.'),
    4: ResultCode('Invalid parameter.')
})

usb = Module('usb', {
    51: ResultCode('USB data transfer in progress.'),
    106: ResultCode('Invalid descriptor.'),
    201: ResultCode('USB device not bound or interface already enabled.')
})

pctl = Module('pctl', {
    223: ResultCode('IsAnyInternetRequestAccepted with the output from GetClientId returned false.')
})

audio = Module('audio', {
    1: ResultCode('Invalid audio device.'),
    2: ResultCode('Operation failed.'),
    3: ResultCode('Invalid sample rate.'),
    4: ResultCode('Buffer size too small.'),
    8: ResultCode('Too many buffers are still unreleased.'),
    10: ResultCode('Invalid channel count.'),
    513: ResultCode('Invalid/unsupported operation.'),
    1536: ResultCode('Invalid handle.'),
    1540: ResultCode('Audio output was already started.')
})

arp = Module('arp', {
    30: ResultCode('Address is NULL.'),
    31: ResultCode('PID is NULL.'),
    42: ResultCode('Already bound'),
    102: ResultCode('Invalid PID.')
})

nifm = Module('nifm', {
    3400: ResultCode('The internet connection you are using requires authentication or a user agreement.' 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/22569/kw/2110-3400'), 
})

ec = Module('ec', {
    20: ResultCode('Unable to start the software.', 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/22539/kw/2164-0020'),
    56: ResultCode('IsAnyInternetRequestAccepted with the output from GetClientId returned false.')
})

jit = Module('jit', {
    2: ResultCode('Bad version.'),
    101: ResultCode('Input NRO/NRR is too large for the storage buffer.'),
    600: ResultCode('Function pointer is not initialized (Control/GenerateCode).'),
    601: ResultCode('DllPlugin not initialized, or plugin NRO already loaded.'),
    602: ResultCode('An error occurred when calling the function pointer with the Control command.'),
})

# known homebrew modules go below here
exosphere = Module('exosphere', {
    1: ResultCode('Not present.'),
    2: ResultCode('Version mismatch.')
})

hbl = Module('homebrew loader', {
    1: ResultCode('Failed to initialize sm.'),
    2: ResultCode('Failed to initialize fs.'),
    3: ResultCode('Next NRO to run was not found. This is usually caused by `hbmenu.nro` not being found on the root of the SD card.'),
    4: ResultCode('Failed to read NRO.'),
    5: ResultCode('NRO header magic is invalid.'),
    6: ResultCode('NRO size does not match size indicated by header.'),
    7: ResultCode('Failed to read the rest of the NRO.'),
    8: ResultCode('Reached an unreachable location in hbloader main(). What are you doing here? This area is off-limits.'),
    9: ResultCode('Unable to set heap size, or heap address was NULL.'),
    10: ResultCode('Failed to create service thread.'),
    12: ResultCode('Unable to create svc session.'),
    13: ResultCode('Failed to start service thread.'),
    15: ResultCode('An error occurred while executing svcReplyAndReceive.'),
    17: ResultCode('Too many (> 1) copy handles from hipcParseRequest.'),
    18: ResultCode('Failed to map process code memory.'),
    19: ResultCode('Failed to set process .text memory permissions.'),
    20: ResultCode('Failed to set process .rodata memory permissions.'),
    21: ResultCode('Failed to set process .data & .bss memory permissions.'),
    24: ResultCode('Failed to unmap process .text.'),
    25: ResultCode('Failed to unmap process .rodata.'),
    26: ResultCode('Failed to unmap process .data and .bss.'),
    39: ResultCode('Attempted to call exit(), which should never happen.'),
    404: ResultCode('Failed to mount SD card.')
})

hb_abi = Module('homebrew ABI', {
    0: ResultCode('End of list.'),
    1: ResultCode('Main thread handle.'),
    2: ResultCode('Next load path.'),
    3: ResultCode('Override heap.'),
    4: ResultCode('Override service.'),
    5: ResultCode('Argv.'),
    6: ResultCode('Syscall available hint.'),
    7: ResultCode('Applet type.'),
    8: ResultCode('Applet workaround.'),
    9: ResultCode('Reserved9.'),
    10: ResultCode('Process handle.'),
    11: ResultCode('Last load result.'),
    12: ResultCode('Alloc pages.'),
    13: ResultCode('Lock region.'),
    14: ResultCode('Random seed.'),
    15: ResultCode('User ID storage.'),
    16: ResultCode('HOS version.')
})

lnx_nvidia = Module('libnx (NVIDIA)', {
    1: ResultCode('Not implemented.'),
    2: ResultCode('Not supported.'),
    3: ResultCode('Not initialized.'),
    4: ResultCode('Bad parameter.'),
    5: ResultCode('Timed out.'),
    6: ResultCode('Insufficient memory.'),
    7: ResultCode('Read-only attribute.'),
    8: ResultCode('Invalid state.'),
    9: ResultCode('Invalid address.'),
    10: ResultCode('Invalid size.'),
    11: ResultCode('Bad value.'),
    13: ResultCode('Already allocated.'),
    14: ResultCode('Busy.'),
    15: ResultCode('Resource error.'),
    16: ResultCode('Count mismatch.'),
    4096: ResultCode('Shared memory too small.'),
    #0x30003: ResultCode('File operation failed.') # This actually belongs to OS.
})

lnx_binder = Module('libnx (binder)', {
    1: ResultCode('Permission denied.'),
    2: ResultCode('Name not found.'),
    11: ResultCode('Would block.'),
    12: ResultCode('No memory.'),
    17: ResultCode('Already exists.'),
    19: ResultCode('No init.'),
    22: ResultCode('Bad value.'),
    32: ResultCode('Dead object.'),
    38: ResultCode('Invalid operation.'),
    61: ResultCode('Not enough data.'),
    74: ResultCode('Unknown transaction.'),
    75: ResultCode('Bad index.'),
    110: ResultCode('Timed out.')
    # TODO: How do I express INT32_MIN in pythonic terms?
    # -(INT32_MIN + 7): ResultCode('Fds not allowed.'),
    # -(INT32_MIN + 2): ResultCode('Failed transaction.'),
    # -(INT32_MIN + 1): ResultCode('Bad type.'),
})

libnx = Module('libnx', {
    1: ResultCode('Bad relocation.'),
    2: ResultCode('Out of memory.'),
    3: ResultCode('Already mapped.'),
    4: ResultCode('Bad getinfo: stack.'),
    5: ResultCode('Bad getinfo: heap.'),
    6: ResultCode('Bad QueryMemory.'),
    7: ResultCode('Aleady initialized.'),
    8: ResultCode('Not initialized.'),
    9: ResultCode('Not found.'),
    10: ResultCode('I/O error.'),
    11: ResultCode('Bad input.'),
    12: ResultCode('Bad re-entry.'),
    13: ResultCode('Buffer producer error.'),
    14: ResultCode('Handle too early.'),
    15: ResultCode('Heap alloc too early.'),
    16: ResultCode('Heap alloc failed.'),
    17: ResultCode('Too many overrides.'),
    18: ResultCode('Parcel error.'),
    19: ResultCode('Bad graphics init.'),
    20: ResultCode('Bad graphics queue buffer.'),
    21: ResultCode('Bad graphics dequeue buffer.'),
    22: ResultCode('Applet command ID not found.'),
    23: ResultCode('Bad applet receive message.'),
    24: ResultCode('Bad applet notify running.'),
    25: ResultCode('Bad applet get current focus state.'),
    26: ResultCode('Bad applet get operation mode.'),
    27: ResultCode('Bad applet get performance mode.'),
    28: ResultCode('Bad USB comms read.'),
    29: ResultCode('Bad USB comms write.'),
    30: ResultCode('Failed to initialize sm.'),
    31: ResultCode('Failed to initialize am.'),
    32: ResultCode('Failed to initialize hid.'),
    33: ResultCode('Failed to initialize fs.'),
    34: ResultCode('Bad getinfo: rng'),
    35: ResultCode('JIT unavailable.'),
    36: ResultCode('Weird kernel.'),
    37: ResultCode('Incompatible system firmware version.'),
    38: ResultCode('Failed to initialize time.'),
    39: ResultCode('Too many dev op tabs.'),
    40: ResultCode('Domain message was of an unknown type.'),
    41: ResultCode('Domain message had too many object IDs.'),
    42: ResultCode('Failed to initialize applet.'),
    43: ResultCode('Failed to initialize apm.'),
    44: ResultCode('Failed to initialize nvinfo.'),
    45: ResultCode('Failed to initialize nvbuf.'),
    46: ResultCode('Libapplet bad exit.'),
    47: ResultCode('Invalid CMIF out header.'),
    48: ResultCode('Should not happen.')
})

applet = Module('applet', {
    1: ResultCode('Exited abnormally.'),
    3: ResultCode('Cancelled.'),
    4: ResultCode('Rejected.'),
    5: ResultCode('Exited unexpectedly.')
})

emuiibo = Module('emuiibo', {
    1: ResultCode('No active virtual Amiibo.'),
    2: ResultCode('Invalid virtual Amiibo.'),
    3: ResultCode('Iterator end reached.'),
    4: ResultCode('Unable to read Mii.')
})


youtube_app = Module('youtube', {
    0: ResultCode('This error typically occurs when your system clock isn\'t set correctly. If the problem persists, try reinstalling YouTube from the Nintendo eShop.')
})

arms_game = Module('ARMS', {
    1021: ResultCode('This error code indicates the connection has likely timed out during a download.', 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/26250/~/error-code%3A-2-aabqa-1021')
})

splatoon_game = Module('Splatoon 2', {
    3400: ResultCode('You have been kicked from the online service due to using exefs/romfs edits.')
})

# We have some modules partially documented, those that aren't have dummy Modules.
modules = {
    1: kernel,
    2: fs,
    3: os,
    4: Module('htcs'),
    5: ncm,
    6: Module('dd'),
    7: dmnt,
    8: lr,
    9: loader,
    10: sf,
    11: hipc,
    13: dmnt,
    15: pm,
    16: ns,
    17: Module('bsdsockets'),
    18: Module('htc'),
    19: Module('tsc'),
    20: kvdb,
    21: sm,
    22: ro,
    23: Module('gc'),
    24: Module('sdmmc'),
    25: Module('ovln'),
    26: spl,
    27: Module('socket'),
    29: Module('htclow'),
    30: Module('bus'),
    31: Module('hfcsfs'),
    32: Module('async'),
    100: Module('ethc'),
    101: i2c,
    102: Module('gpio'),
    103: Module('uart'),
    105: settings,
    107: Module('wlan'),
    108: Module('xcd'),
    110: nifm,
    111: Module('hwopus'),
    113: Module('bluetooth'),
    114: vi,
    115: nfp,
    116: time,
    117: Module('fgm'),
    118: Module('oe'),
    120: Module('pcie'),
    121: friends,
    122: bcat,
    123: ssl,
    124: account,
    125: Module('news'),
    126: mii,
    127: Module('nfc'),
    128: am,
    129: prepo,
    130: Module('ahid'),
    132: Module('qlaunch'),
    133: pcv,
    134: Module('omm'),
    135: Module('bpc'),
    136: Module('psm'),
    137: nim,
    138: psc,
    139: Module('tc'),
    140: usb,
    141: Module('nsd'),
    142: pctl,
    143: Module('btm'),
    144: applet,
    145: Module('es'),
    146: Module('ngc'),
    147: erpt,
    148: Module('apm'),
    149: Module('cec'),
    150: Module('profiler'),
    151: Module('eupld'),
    153: audio,
    154: Module('npns'),
    155: Module('npns xmpp stream'),
    157: arp,
    158: updater,
    159: Module('swkbd'),
    161: Module('mifare'),
    162: userland_assert,
    163: fatal,
    164: ec,
    165: Module('spsm'),
    167: Module('bgtc'),
    168: creport,
    175: jit,
    178: Module('pdm'),
    179: Module('olsc'),
    180: Module('srepo'),
    181: dauth,
    183: dbg,
    187: Module('sasbus'),
    189: Module('pwm'),
    191: Module('rtc'),
    192: Module('regulator'),
    193: Module('led'),
    197: Module('clkrst'),
    198: calibration,
    202: Module('hid'),
    203: Module('ldn'),
    205: Module('irsensor'),
    206: capsrv,
    208: Module('manu'),
    210: Module('web'),
    211: Module('lcs'),
    212: Module('grc'),
    214: Module('album'),
    216: Module('migration'),
    218: Module('hidbus'),
    223: Module('websocket'),
    228: Module('pgl'),
    229: Module('notification'),
    230: Module('ins'),
    231: Module('lp2p'),

    800: web_applet,
    809: web_applet,
    810: web_applet,
    811: web_applet,
    'arvha': youtube_app,
    'aabqa': arms_game,
    'aab6a': splatoon_game,

    # Add non-nintendo modules below here.
    345: libnx,
    346: hb_abi,
    347: hbl,
    348: lnx_nvidia,
    349: lnx_binder,
    352: emuiibo,
    416: Module('SwitchPresence-Rewritten'),
    444: exosphere,
    789: Module('SwitchPresence-Old-Random'),
}

# regex for result code format "XXXX-YYYY"
RE = re.compile(r'2\d{3}\-\d{4}')

# regex for result code format "2-BBBBB-CCCC"
# The first digit always appears to be "2" for games/applications.
RE_APP = re.compile(r'2-[a-zA-Z]{5}-\d{4}')

CONSOLE_NAME = 'Nintendo Switch'

# Suggested color to use if displaying information through a Discord bot's embed
COLOR = 0xE60012

def is_valid(error):
    err_int = None
    if error.startswith('0x'):
        err_int = int(error, 16)
    if err_int:
        return not err_int & 0x80000000
    return RE.match(error) or RE_APP.match(error)

def err2hex(error):
    if RE.match(error):
        module = int(error[:4]) - 2000
        desc = int(error[5:9])
        code = (desc << 9) + module
        return hex(code)
    return 'Invalid format. The only supported error code format is `XXXX-YYYY`.'

def hex2err(error):
    if error.startswith('0x'):
        error = error[2:]
    error = int(error, 16)
    module = error & 0x1FF
    desc = (error >> 9) & 0x3FFF
    code = f'{module + 2000:04}-{desc:04}'
    return code

def get(error):
    if RE_APP.match(error):
        subs = error.split('-')
        mod = subs[1].casefold()
        code = int(subs[2], 10)
    elif not error.startswith('0x'):
        mod = int(error[:4], 10) - 2000
        code = int(error[5:9], 10)
    else:
        err_int = int(error, 16)
        mod = err_int & 0x1FF
        code = (err_int >> 9 & 0x3FFF)

    if mod in modules:
        if not modules[mod].data:
            return CONSOLE_NAME, modules[mod].name, NO_RESULTS_FOUND, COLOR
        ret = modules[mod].get_error(code)
        ret.code = code
        ret.summary = modules[mod].get_level(code)
        return CONSOLE_NAME, modules[mod].name, modules[mod].get_error(code), COLOR

    return CONSOLE_NAME, None, UNKNOWN_MODULE, COLOR


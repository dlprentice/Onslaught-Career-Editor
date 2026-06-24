/* address: 0x0056bdc9 */
/* name: CDXTexture__Unk_0056bdc9 */
/* signature: void __cdecl CDXTexture__Unk_0056bdc9(int param_1) */


void __cdecl CDXTexture__Unk_0056bdc9(int param_1)

{
  if ((param_1 != 0) && (*(undefined **)(param_1 + 0xc) != &DAT_009d0c28)) {
    CMeshCollisionVolume__Unk_0055f085((int)*(undefined **)(param_1 + 0xc));
    CMeshCollisionVolume__Unk_0055f085(*(int *)(param_1 + 0x10));
    CMeshCollisionVolume__Unk_0055f085(*(int *)(param_1 + 0x14));
    CMeshCollisionVolume__Unk_0055f085(*(int *)(param_1 + 0x18));
    CMeshCollisionVolume__Unk_0055f085(*(int *)(param_1 + 0x1c));
    CMeshCollisionVolume__Unk_0055f085(*(int *)(param_1 + 0x20));
    CMeshCollisionVolume__Unk_0055f085(*(int *)(param_1 + 0x24));
  }
  return;
}

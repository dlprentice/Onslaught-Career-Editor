/* address: 0x00591340 */
/* name: CMeshCollisionVolume__Unk_00591340 */
/* signature: int __stdcall CMeshCollisionVolume__Unk_00591340(void * param_1, int param_2) */


int CMeshCollisionVolume__Unk_00591340(void *param_1,int param_2)

{
  undefined4 *puVar1;
  int iVar2;

  iVar2 = *(int *)((int)param_1 + 0x14);
  if ((iVar2 != 200) && (iVar2 != 0xc9)) {
    puVar1 = *(undefined4 **)param_1;
    puVar1[5] = 0x14;
    puVar1[6] = iVar2;
    (*(code *)*puVar1)(param_1);
  }
  iVar2 = CMeshCollisionVolume__Helper_005911d0(param_1);
  if (iVar2 == 1) {
    iVar2 = 1;
  }
  else if (iVar2 == 2) {
    if (param_2 != 0) {
      puVar1 = *(undefined4 **)param_1;
      puVar1[5] = 0x33;
      (*(code *)*puVar1)(param_1);
    }
    CDXTexture__Unk_0059c5d0((int)param_1);
    return 2;
  }
  return iVar2;
}

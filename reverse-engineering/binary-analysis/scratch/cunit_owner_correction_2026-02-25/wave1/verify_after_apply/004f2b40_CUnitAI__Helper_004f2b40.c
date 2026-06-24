/* address: 0x004f2b40 */
/* name: CUnitAI__Helper_004f2b40 */
/* signature: void CUnitAI__Helper_004f2b40(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CUnitAI__Helper_004f2b40(void)

{
  void *pvVar1;
  void *this;
  void *pvVar2;
  char local_100 [256];

  DAT_0083d9b8 = 0;
  DebugTrace(s_CTexture__FreeLevelResources___c_00633108);
  pvVar1 = DAT_0083d9b0;
  pvVar2 = DAT_0083d9b0;
  if (DAT_0083d9b4 != 0) {
    *(int *)(DAT_0083d9b4 + 0xa4) = *(int *)(DAT_0083d9b4 + 0xa4) + -1;
    DAT_0083d9b4 = 0;
    pvVar1 = DAT_0083d9b0;
    pvVar2 = DAT_0083d9b0;
  }
  while (this = pvVar1, DAT_0083d9b0 = pvVar2, this != (void *)0x0) {
    pvVar1 = *(void **)((int)this + 0xa0);
    if (*(int *)((int)this + 0xa4) == 0) {
      CTexture__Release(this);
      pvVar2 = DAT_0083d9b0;
    }
  }
  if (pvVar2 != (void *)0x0) {
    DebugTrace(s__________________________________006330e0);
    DebugTrace(s_Texture_end_of_level_resource_le_006330b8);
    DebugTrace(s__________________________________00633090);
    do {
      sprintf(local_100,s_Texture___s__leaked___refcount___00632fcc);
      DebugTrace(local_100);
      pvVar2 = *(void **)((int)pvVar2 + 0xa0);
    } while (pvVar2 != (void *)0x0);
    DebugTrace(s__________________________________00633068);
    return;
  }
  DebugTrace(s_No_end_of_level_texture_resource_00633040);
  return;
}

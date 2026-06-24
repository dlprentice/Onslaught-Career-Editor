/* address: 0x004950f0 */
/* name: CMeshPart__Helper_004950f0 */
/* signature: int __cdecl CMeshPart__Helper_004950f0(int param_1) */


int __cdecl CMeshPart__Helper_004950f0(int param_1)

{
  int iVar1;
  int iVar2;

  iVar2 = 0;
  if (0 < *(int *)(param_1 + 0x15c)) {
    do {
      iVar1 = CMCBuggy__Helper_0056e170
                        ((void *)(*(int *)(*(int *)(param_1 + 0x160) + iVar2 * 4) + 0xdc),
                         &DAT_0062896c,(void *)0x4);
      if (iVar1 == 0) {
        return 1;
      }
      iVar2 = iVar2 + 1;
    } while (iVar2 < *(int *)(param_1 + 0x15c));
  }
  return 0;
}

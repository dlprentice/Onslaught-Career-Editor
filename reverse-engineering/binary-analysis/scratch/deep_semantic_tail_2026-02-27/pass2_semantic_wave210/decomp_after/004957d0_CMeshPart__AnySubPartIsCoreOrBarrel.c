/* address: 0x004957d0 */
/* name: CMeshPart__AnySubPartIsCoreOrBarrel */
/* signature: int __cdecl CMeshPart__AnySubPartIsCoreOrBarrel(int param_1) */


int __cdecl CMeshPart__AnySubPartIsCoreOrBarrel(int param_1)

{
  int iVar1;
  int iVar2;

  iVar2 = 0;
  if (0 < *(int *)(param_1 + 0x15c)) {
    do {
      iVar1 = stricmp((char *)(*(int *)(*(int *)(param_1 + 0x160) + iVar2 * 4) + 0xdc),&DAT_0062dd20
                     );
      if (iVar1 == 0) {
        return 1;
      }
      iVar1 = CMCBuggy__Helper_0056e170
                        ((void *)(*(int *)(*(int *)(param_1 + 0x160) + iVar2 * 4) + 0xdc),
                         s_barrel_0062dd18,(void *)0x6);
      if (iVar1 == 0) {
        return 1;
      }
      iVar2 = iVar2 + 1;
    } while (iVar2 < *(int *)(param_1 + 0x15c));
  }
  return 0;
}

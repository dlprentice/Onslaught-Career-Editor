/* address: 0x0049f670 */
/* name: CUnitAI__Unk_0049f670 */
/* signature: int __cdecl CUnitAI__Unk_0049f670(int param_1) */


int __cdecl CUnitAI__Unk_0049f670(int param_1)

{
  int iVar1;
  int iVar2;

  iVar2 = 0;
  if (0 < *(int *)(param_1 + 0x15c)) {
    do {
      iVar1 = stricmp((char *)(*(int *)(*(int *)(param_1 + 0x160) + iVar2 * 4) + 0xdc),&DAT_0062e0cc
                     );
      if (iVar1 == 0) {
        return 1;
      }
      iVar1 = CDXTexture__Unk_0056e170
                        ((void *)(*(int *)(*(int *)(param_1 + 0x160) + iVar2 * 4) + 0xdc),
                         s_barrel_0062dd18,(void *)0x6);
      if (iVar1 == 0) {
        return 1;
      }
      iVar1 = stricmp((char *)(*(int *)(*(int *)(param_1 + 0x160) + iVar2 * 4) + 0xdc),
                      s_spinner_0062e0c4);
      if (iVar1 == 0) {
        return 1;
      }
      iVar1 = CDXTexture__Unk_0056e170
                        ((void *)(*(int *)(*(int *)(param_1 + 0x160) + iVar2 * 4) + 0xdc),
                         &PTR_DAT_0062e0c0,(void *)0x3);
      if (iVar1 == 0) {
        return 1;
      }
      iVar2 = iVar2 + 1;
    } while (iVar2 < *(int *)(param_1 + 0x15c));
  }
  return 0;
}

/* address: 0x00496910 */
/* name: CUnitAI__Unk_00496910 */
/* signature: int __cdecl CUnitAI__Unk_00496910(int param_1) */


int __cdecl CUnitAI__Unk_00496910(int param_1)

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
      iVar2 = iVar2 + 1;
    } while (iVar2 < *(int *)(param_1 + 0x15c));
  }
  return 0;
}

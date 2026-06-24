/* address: 0x00496f60 */
/* name: CUnitAI__Unk_00496f60 */
/* signature: bool __cdecl CUnitAI__Unk_00496f60(int param_1) */


bool __cdecl CUnitAI__Unk_00496f60(int param_1)

{
  int iVar1;

  iVar1 = stricmp((char *)(param_1 + 0xdc),&DAT_0062dd20);
  if (iVar1 == 0) {
    return false;
  }
  iVar1 = CDXTexture__Unk_0056e170((char *)(param_1 + 0xdc),s_barrel_0062dd18,(void *)0x6);
  return iVar1 != 0;
}

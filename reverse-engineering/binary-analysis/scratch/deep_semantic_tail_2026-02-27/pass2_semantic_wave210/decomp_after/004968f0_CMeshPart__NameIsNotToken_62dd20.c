/* address: 0x004968f0 */
/* name: CMeshPart__NameIsNotToken_62dd20 */
/* signature: bool __cdecl CMeshPart__NameIsNotToken_62dd20(int param_1) */


bool __cdecl CMeshPart__NameIsNotToken_62dd20(int param_1)

{
  int iVar1;

  iVar1 = stricmp((char *)(param_1 + 0xdc),&DAT_0062dd20);
  return iVar1 != 0;
}

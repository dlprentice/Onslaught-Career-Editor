/* address: 0x00472240 */
/* name: CGame__Unk_00472240 */
/* signature: void __cdecl CGame__Unk_00472240(int param_1, void * param_2) */


void __cdecl CGame__Unk_00472240(int param_1,void *param_2)

{
  int iVar1;

  iVar1 = vsprintf(*(char **)(param_1 + 10000),param_2,&stack0x0000000c);
  *(int *)(param_1 + 10000) = *(int *)(param_1 + 10000) + iVar1;
  return;
}

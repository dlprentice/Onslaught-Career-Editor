/* address: 0x0055f2e8 */
/* name: CRT__WcsCmp */
/* signature: int __cdecl CRT__WcsCmp(void * param_1, void * param_2) */


int __cdecl CRT__WcsCmp(void *param_1,void *param_2)

{
  int iVar1;
  ushort uVar2;

  uVar2 = *(ushort *)param_2;
  while ((iVar1 = (uint)*(ushort *)param_1 - (uint)uVar2, iVar1 == 0 && (uVar2 != 0))) {
    param_1 = (void *)((int)param_1 + 2);
    param_2 = (void *)((int)param_2 + 2);
    uVar2 = *(ushort *)param_2;
  }
  if (iVar1 < 0) {
    return -1;
  }
  if (0 < iVar1) {
    iVar1 = 1;
  }
  return iVar1;
}

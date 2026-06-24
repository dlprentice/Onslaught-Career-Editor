/* address: 0x0056d4a6 */
/* name: CRT__UIntAddWithOverflowCheck */
/* signature: int __cdecl CRT__UIntAddWithOverflowCheck(uint param_1, uint param_2, void * param_3) */


int __cdecl CRT__UIntAddWithOverflowCheck(uint param_1,uint param_2,void *param_3)

{
  uint uVar1;
  int iVar2;

  iVar2 = 0;
  uVar1 = param_1 + param_2;
  if ((uVar1 < param_1) || (uVar1 < param_2)) {
    iVar2 = 1;
  }
  *(uint *)param_3 = uVar1;
  return iVar2;
}

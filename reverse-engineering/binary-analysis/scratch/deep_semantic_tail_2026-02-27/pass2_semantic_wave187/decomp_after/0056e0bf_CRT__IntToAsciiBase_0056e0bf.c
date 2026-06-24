/* address: 0x0056e0bf */
/* name: CRT__IntToAsciiBase_0056e0bf */
/* signature: int __cdecl CRT__IntToAsciiBase_0056e0bf(int param_1, int param_2, int param_3) */


int __cdecl CRT__IntToAsciiBase_0056e0bf(int param_1,int param_2,int param_3)

{
  int iVar1;

  if ((param_3 == 10) && (param_1 < 0)) {
    iVar1 = 1;
    param_3 = 10;
  }
  else {
    iVar1 = 0;
  }
  CRT__UIntToAsciiBase(param_1,(void *)param_2,param_3,iVar1);
  return param_2;
}

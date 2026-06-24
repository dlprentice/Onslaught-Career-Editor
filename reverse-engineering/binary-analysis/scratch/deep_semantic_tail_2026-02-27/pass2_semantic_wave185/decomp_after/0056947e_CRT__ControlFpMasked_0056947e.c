/* address: 0x0056947e */
/* name: CRT__ControlFpMasked_0056947e */
/* signature: void __cdecl CRT__ControlFpMasked_0056947e(uint param_1, uint param_2) */


void __cdecl CRT__ControlFpMasked_0056947e(uint param_1,uint param_2)

{
  CRT__ControlFp(param_1,param_2 & 0xfff7ffff);
  return;
}

/* address: 0x005693fe */
/* name: CRT__IsWritablePtr */
/* signature: bool __cdecl CRT__IsWritablePtr(int param_1, uint param_2) */


bool __cdecl CRT__IsWritablePtr(int param_1,uint param_2)

{
  BOOL BVar1;

  BVar1 = IsBadWritePtr((LPVOID)param_1,param_2);
  return BVar1 == 0;
}

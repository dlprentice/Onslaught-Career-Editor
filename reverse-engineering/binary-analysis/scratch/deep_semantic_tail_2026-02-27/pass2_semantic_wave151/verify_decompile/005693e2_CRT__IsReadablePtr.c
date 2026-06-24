/* address: 0x005693e2 */
/* name: CRT__IsReadablePtr */
/* signature: bool __cdecl CRT__IsReadablePtr(void * param_1, uint param_2) */


bool __cdecl CRT__IsReadablePtr(void *param_1,uint param_2)

{
  BOOL BVar1;

  BVar1 = IsBadReadPtr(param_1,param_2);
  return BVar1 == 0;
}

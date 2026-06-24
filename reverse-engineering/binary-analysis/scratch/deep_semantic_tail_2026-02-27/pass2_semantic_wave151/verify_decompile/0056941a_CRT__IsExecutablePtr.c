/* address: 0x0056941a */
/* name: CRT__IsExecutablePtr */
/* signature: bool __cdecl CRT__IsExecutablePtr(int param_1) */


bool __cdecl CRT__IsExecutablePtr(int param_1)

{
  BOOL BVar1;

  BVar1 = IsBadCodePtr((FARPROC)param_1);
  return BVar1 == 0;
}

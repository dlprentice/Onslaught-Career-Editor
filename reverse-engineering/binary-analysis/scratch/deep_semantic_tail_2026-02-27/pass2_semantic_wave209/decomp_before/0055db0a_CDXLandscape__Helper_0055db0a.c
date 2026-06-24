/* address: 0x0055db0a */
/* name: CDXLandscape__Helper_0055db0a */
/* signature: void __stdcall CDXLandscape__Helper_0055db0a(int param_1, int param_2, int param_3, void * param_4) */


void CDXLandscape__Helper_0055db0a(int param_1,int param_2,int param_3,void *param_4)

{
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  puStack_c = &DAT_005e5aa8;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  local_8 = 0;
  ExceptionList = &local_14;
  while( true ) {
    param_3 = param_3 + -1;
    if (param_3 < 0) break;
    (*param_4)();
  }
  local_8 = 0xffffffff;
  CRT__EhVectorDestructorIterator_IfNoException();
  ExceptionList = local_14;
  return;
}

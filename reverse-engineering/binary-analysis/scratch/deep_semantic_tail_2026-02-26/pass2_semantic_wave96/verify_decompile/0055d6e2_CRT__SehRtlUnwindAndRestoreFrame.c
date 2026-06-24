/* address: 0x0055d6e2 */
/* name: CRT__SehRtlUnwindAndRestoreFrame */
/* signature: void __stdcall CRT__SehRtlUnwindAndRestoreFrame(int param_1, int param_2) */


void CRT__SehRtlUnwindAndRestoreFrame(int param_1,int param_2)

{
  void *pvVar1;

  pvVar1 = ExceptionList;
  RtlUnwind((PVOID)param_1,(PVOID)0x55d70a,(PEXCEPTION_RECORD)param_2,(PVOID)0x0);
  *(uint *)(param_2 + 4) = *(uint *)(param_2 + 4) & 0xfffffffd;
  *(void **)pvVar1 = ExceptionList;
  ExceptionList = pvVar1;
  return;
}

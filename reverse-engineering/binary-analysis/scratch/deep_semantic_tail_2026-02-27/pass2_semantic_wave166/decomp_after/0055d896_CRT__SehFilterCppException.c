/* address: 0x0055d896 */
/* name: CRT__SehFilterCppException */
/* signature: int __cdecl CRT__SehFilterCppException(int param_1, int param_2, int param_3) */


int __cdecl CRT__SehFilterCppException(int param_1,int param_2,int param_3)

{
  int iVar1;

  if ((*(uint *)(param_1 + 4) & 0x66) != 0) {
    *(undefined4 *)(param_2 + 0x24) = 1;
    return 1;
  }
  CRT__SehDispatchWithScopeTable();
  if (*(int *)(param_2 + 0x24) == 0) {
    CRT__SehRtlUnwindAndRestoreFrame(param_2,param_1);
  }
                    /* WARNING: Could not recover jumptable at 0x0055d900. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  iVar1 = (**(code **)(param_2 + 0x18))();
  return iVar1;
}

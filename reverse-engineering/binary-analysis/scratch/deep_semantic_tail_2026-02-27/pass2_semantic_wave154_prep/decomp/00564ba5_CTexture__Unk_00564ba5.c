/* address: 0x00564ba5 */
/* name: CTexture__Unk_00564ba5 */
/* signature: int __stdcall CTexture__Unk_00564ba5(void * param_1) */


int CTexture__Unk_00564ba5(void *param_1)

{
  int *piVar1;
  bool bVar2;
  int extraout_EAX;
  undefined3 extraout_var;
  int iVar3;

  piVar1 = *(int **)param_1;
  if (((*piVar1 == -0x1f928c9d) && (piVar1[4] == 3)) && (piVar1[5] == 0x19930520)) {
    CDXTexture__InvokeTlsCleanupCallbackAndFinalize();
    return extraout_EAX;
  }
  if ((DAT_009d0980 != (code *)0x0) &&
     (bVar2 = CRT__IsExecutablePtr((int)DAT_009d0980), CONCAT31(extraout_var,bVar2) != 0)) {
    iVar3 = (*DAT_009d0980)(param_1);
    return iVar3;
  }
  return 0;
}

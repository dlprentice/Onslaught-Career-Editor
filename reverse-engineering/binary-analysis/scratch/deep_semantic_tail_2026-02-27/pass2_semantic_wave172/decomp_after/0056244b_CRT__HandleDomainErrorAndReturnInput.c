/* address: 0x0056244b */
/* name: CRT__HandleDomainErrorAndReturnInput */
/* signature: double __cdecl CRT__HandleDomainErrorAndReturnInput(int param_1, double param_2, int param_3) */


double __cdecl CRT__HandleDomainErrorAndReturnInput(int param_1,double param_2,int param_3)

{
  undefined4 *puVar1;
  float10 extraout_ST0;
  undefined4 in_stack_00000008;

  if (DAT_006561f0 == 0) {
    CDXTexture__ValidateSourceAndSetLoadErrorClass((void *)0x1,(void *)param_1);
    return (double)extraout_ST0;
  }
  puVar1 = (undefined4 *)CTexture__Helper_00567aa8();
  *puVar1 = 0x21;
  CRT__GetFpuControlWord();
  return (double)CONCAT44(param_2._0_4_,in_stack_00000008);
}

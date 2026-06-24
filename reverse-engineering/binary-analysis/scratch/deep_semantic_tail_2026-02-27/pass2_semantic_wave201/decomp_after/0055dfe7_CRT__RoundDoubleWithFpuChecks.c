/* address: 0x0055dfe7 */
/* name: CRT__RoundDoubleWithFpuChecks */
/* signature: double __cdecl CRT__RoundDoubleWithFpuChecks(double param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __cdecl CRT__RoundDoubleWithFpuChecks(double param_1)

{
  uint uVar1;
  int iVar2;
  int unaff_ESI;
  float10 fVar3;
  float10 extraout_ST0;
  double dVar4;
  uint uVar5;

  uVar1 = CRT__GetFpuControlWord();
  uVar5 = (uint)((ulonglong)param_1 >> 0x20);
  if ((param_1._6_2_ & 0x7ff0) == 0x7ff0) {
    iVar2 = CFastVB__ClassifyDoubleWords(SUB84(param_1,0),uVar5);
    if (0 < iVar2) {
      if (iVar2 < 3) {
        CRT__GetFpuControlWord();
        fVar3 = (float10)param_1;
        goto LAB_0055e0b2;
      }
      if (iVar2 == 3) {
        dVar4 = CRT__HandleDomainErrorAndReturnInput(0xb,(double)CONCAT44(uVar1,uVar5),unaff_ESI);
        fVar3 = (float10)dVar4;
        goto LAB_0055e0b2;
      }
    }
  }
  else {
    fVar3 = (float10)__frnd();
    if (((double)fVar3 == param_1) || ((uVar1 & 0x20) != 0)) {
      CRT__GetFpuControlWord();
      fVar3 = (float10)(double)fVar3;
      goto LAB_0055e0b2;
    }
  }
  CRT__HandleFloatingPointExceptionByFlags();
  fVar3 = extraout_ST0;
LAB_0055e0b2:
  return (double)fVar3;
}

/* address: 0x00561590 */
/* name: CRT__Exp2FromFpuCore_00561590 */
/* signature: int CRT__Exp2FromFpuCore_00561590(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__Exp2FromFpuCore_00561590(void)

{
  int in_EAX;
  float10 in_ST0;
  float10 fVar1;

  fVar1 = (float10)f2xm1(-(ROUND(in_ST0) - in_ST0));
  fscale((float10)1 + fVar1,ROUND(in_ST0));
  return in_EAX;
}

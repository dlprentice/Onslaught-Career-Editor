/* address: 0x0055f380 */
/* name: CRT__AcosClassifyAndDispatch */
/* signature: void CRT__AcosClassifyAndDispatch(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__AcosClassifyAndDispatch(void)

{
  float10 in_ST0;
  double dVar1;

  dVar1 = (double)in_ST0;
  CRT__ExtractFiniteExponentMaskOrPassThrough_00561618
            (SUB84(dVar1,0),(uint)((ulonglong)dVar1 >> 0x20));
  CRT__AcosCoreWithFpuGuards(SUB84(dVar1,0),(uint)((ulonglong)dVar1 >> 0x20));
  return;
}

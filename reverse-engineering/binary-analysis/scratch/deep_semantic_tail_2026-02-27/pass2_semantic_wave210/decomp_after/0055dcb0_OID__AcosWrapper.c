/* address: 0x0055dcb0 */
/* name: OID__AcosWrapper */
/* signature: void OID__AcosWrapper(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void OID__AcosWrapper(void)

{
  float10 in_ST0;
  double dVar1;

  dVar1 = (double)in_ST0;
  CRT__ExtractFiniteExponentMaskOrPassThrough_00561618
            (SUB84(dVar1,0),(uint)((ulonglong)dVar1 >> 0x20));
  CRT__Acos(SUB84(dVar1,0),(uint)((ulonglong)dVar1 >> 0x20));
  return;
}

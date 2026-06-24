/* address: 0x0040d1a0 */
/* name: CMonitor__Helper_0040d1a0 */
/* signature: double __fastcall CMonitor__Helper_0040d1a0(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CMonitor__Helper_0040d1a0(void *param_1)

{
  float10 extraout_ST0;

  if (_DAT_005d856c <
      SQRT(*(float *)((int)param_1 + 8) * *(float *)((int)param_1 + 8) +
           *(float *)((int)param_1 + 4) * *(float *)((int)param_1 + 4) +
           *(float *)param_1 * *(float *)param_1)) {
    OID__Helper_0055dcb0();
    return (double)extraout_ST0;
  }
  return (double)_DAT_005d856c;
}

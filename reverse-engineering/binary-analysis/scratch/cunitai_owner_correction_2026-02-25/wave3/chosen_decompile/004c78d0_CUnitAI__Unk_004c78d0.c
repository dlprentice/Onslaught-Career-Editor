/* address: 0x004c78d0 */
/* name: CUnitAI__Unk_004c78d0 */
/* signature: double __fastcall CUnitAI__Unk_004c78d0(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CUnitAI__Unk_004c78d0(void *param_1)

{
  return (double)(_DAT_005d8568 /
                 SQRT(*(float *)((int)param_1 + 8) * *(float *)((int)param_1 + 8) +
                      *(float *)((int)param_1 + 4) * *(float *)((int)param_1 + 4) +
                      *(float *)param_1 * *(float *)param_1));
}

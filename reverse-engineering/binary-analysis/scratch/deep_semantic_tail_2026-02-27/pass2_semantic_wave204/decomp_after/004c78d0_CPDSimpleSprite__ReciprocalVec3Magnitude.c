/* address: 0x004c78d0 */
/* name: CPDSimpleSprite__ReciprocalVec3Magnitude */
/* signature: double __fastcall CPDSimpleSprite__ReciprocalVec3Magnitude(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CPDSimpleSprite__ReciprocalVec3Magnitude(void *param_1)

{
  return (double)(_DAT_005d8568 /
                 SQRT(*(float *)((int)param_1 + 8) * *(float *)((int)param_1 + 8) +
                      *(float *)((int)param_1 + 4) * *(float *)((int)param_1 + 4) +
                      *(float *)param_1 * *(float *)param_1));
}

/* address: 0x0049bc40 */
/* name: MathMatrix3x3__Determinant */
/* signature: double __fastcall MathMatrix3x3__Determinant(void * param_1) */


double __fastcall MathMatrix3x3__Determinant(void *param_1)

{
  return (double)((*(float *)((int)param_1 + 0x10) * *(float *)((int)param_1 + 0x24) -
                  *(float *)((int)param_1 + 0x20) * *(float *)((int)param_1 + 0x14)) *
                  *(float *)((int)param_1 + 8) +
                 ((*(float *)((int)param_1 + 0x14) * *(float *)((int)param_1 + 0x28) -
                  *(float *)((int)param_1 + 0x18) * *(float *)((int)param_1 + 0x24)) *
                  *(float *)param_1 -
                 (*(float *)((int)param_1 + 0x10) * *(float *)((int)param_1 + 0x28) -
                 *(float *)((int)param_1 + 0x20) * *(float *)((int)param_1 + 0x18)) *
                 *(float *)((int)param_1 + 4)));
}

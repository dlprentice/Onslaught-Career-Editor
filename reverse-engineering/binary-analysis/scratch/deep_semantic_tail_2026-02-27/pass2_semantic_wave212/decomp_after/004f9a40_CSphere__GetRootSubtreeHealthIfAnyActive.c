/* address: 0x004f9a40 */
/* name: CSphere__GetRootSubtreeHealthIfAnyActive */
/* signature: double __fastcall CSphere__GetRootSubtreeHealthIfAnyActive(int param_1) */


double __fastcall CSphere__GetRootSubtreeHealthIfAnyActive(int param_1)

{
  double dVar1;

  if (*(int *)(param_1 + 0x178) == 0) {
    return (double)*(float *)(param_1 + 0xf8);
  }
  dVar1 = CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive
                    (*(int *)(param_1 + 0x178));
  return dVar1;
}

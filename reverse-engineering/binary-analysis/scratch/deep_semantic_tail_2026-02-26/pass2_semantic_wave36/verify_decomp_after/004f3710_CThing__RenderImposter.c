/* address: 0x004f3710 */
/* name: CThing__RenderImposter */
/* signature: void __fastcall CThing__RenderImposter(int param_1) */


void __fastcall CThing__RenderImposter(int param_1)

{
  if ((*(int **)(param_1 + 0x30) != (int *)0x0) && ((*(byte *)(param_1 + 0x2c) & 8) == 0)) {
                    /* WARNING: Could not recover jumptable at 0x004f3721. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(**(int **)(param_1 + 0x30) + 0xc))();
    return;
  }
  return;
}

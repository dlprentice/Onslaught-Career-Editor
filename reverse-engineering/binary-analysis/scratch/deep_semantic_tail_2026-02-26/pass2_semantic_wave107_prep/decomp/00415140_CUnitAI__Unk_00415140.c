/* address: 0x00415140 */
/* name: CUnitAI__Unk_00415140 */
/* signature: void __fastcall CUnitAI__Unk_00415140(void * param_1) */


void __fastcall CUnitAI__Unk_00415140(void *param_1)

{
  if (*(int *)((int)param_1 + 0x264) != 1) {
    CConsole__Printf(&DAT_0066f580,s_landed______________006239ac);
    *(undefined4 *)((int)param_1 + 300) = 0;
    (**(code **)(*(int *)param_1 + 0x110))();
    (**(code **)(*(int *)param_1 + 0x100))();
    if (*(int *)((int)param_1 + 0x214) != 0) {
      (**(code **)(*(int *)param_1 + 0x148))();
    }
    *(undefined4 *)((int)param_1 + 0x264) = 1;
  }
  return;
}

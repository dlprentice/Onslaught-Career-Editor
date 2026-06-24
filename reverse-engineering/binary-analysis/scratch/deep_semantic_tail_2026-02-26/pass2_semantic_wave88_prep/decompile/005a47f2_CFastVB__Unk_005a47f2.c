/* address: 0x005a47f2 */
/* name: CFastVB__Unk_005a47f2 */
/* signature: void __stdcall CFastVB__Unk_005a47f2(void * param_1, void * param_2, void * param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__Unk_005a47f2(void *param_1,void *param_2,void *param_3)

{
  undefined8 extraout_MM0;
  undefined8 uVar1;

  uVar1 = *(undefined8 *)((int)param_1 + 8);
  if (param_2 != (void *)0x0) {
    *(undefined8 *)param_2 = *(undefined8 *)param_1;
    *(int *)((int)param_2 + 8) = (int)uVar1;
  }
  if (param_3 != (void *)0x0) {
    CFastVB__Unk_005b86c0();
    uVar1 = PackedFloatingMUL(extraout_MM0,_DAT_005ef108);
    *(int *)param_3 = (int)uVar1;
  }
  FastExitMediaState();
  return;
}

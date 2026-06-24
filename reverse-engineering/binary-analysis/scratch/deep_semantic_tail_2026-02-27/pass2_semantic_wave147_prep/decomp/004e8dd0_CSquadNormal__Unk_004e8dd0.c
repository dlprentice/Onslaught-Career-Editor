/* address: 0x004e8dd0 */
/* name: CSquadNormal__Unk_004e8dd0 */
/* signature: int __fastcall CSquadNormal__Unk_004e8dd0(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CSquadNormal__Unk_004e8dd0(void *param_1)

{
  int *piVar1;
  float10 fVar2;

  piVar1 = (int *)(**(code **)(*(int *)param_1 + 0x128))();
  if (piVar1 != (int *)0x0) {
    fVar2 = (float10)(**(code **)(*piVar1 + 0x3c))();
    if (((float10)_DAT_005d856c < fVar2) && (*(int *)((int)param_1 + 0x9c) == 0)) {
      return 1;
    }
  }
  return 0;
}

/* address: 0x0042e750 */
/* name: CGame__DispatchVibrationWithCareerGate */
/* signature: void __thiscall CGame__DispatchVibrationWithCareerGate(void * this, void * param_1, float param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CGame__DispatchVibrationWithCareerGate(void *this,void *param_1,float param_2,int param_3)

{
  if ((DAT_008a9ac0 == 3) || ((float)param_1 == _DAT_005d856c)) {
    if ((&CAREER_mVibration_P1)[(int)param_2] != 0) {
      (**(code **)(*(int *)this + 4))(param_1);
      return;
    }
    (**(code **)(*(int *)this + 4))(0);
  }
  return;
}

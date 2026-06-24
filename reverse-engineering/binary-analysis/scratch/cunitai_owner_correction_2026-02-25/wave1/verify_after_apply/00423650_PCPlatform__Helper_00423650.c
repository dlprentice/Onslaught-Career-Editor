/* address: 0x00423650 */
/* name: PCPlatform__Helper_00423650 */
/* signature: float * __fastcall PCPlatform__Helper_00423650(void * param_1) */


float * __fastcall PCPlatform__Helper_00423650(void *param_1)

{
  LARGE_INTEGER *lpFrequency;
  BOOL BVar1;

  lpFrequency = (LARGE_INTEGER *)((int)param_1 + 0x18);
  BVar1 = QueryPerformanceFrequency(lpFrequency);
  if (BVar1 == 0) {
    (lpFrequency->s).LowPart = 1000;
    *(undefined4 *)((int)param_1 + 0x1c) = 0;
  }
  *(float *)param_1 = (float)(longlong)*lpFrequency;
  return param_1;
}

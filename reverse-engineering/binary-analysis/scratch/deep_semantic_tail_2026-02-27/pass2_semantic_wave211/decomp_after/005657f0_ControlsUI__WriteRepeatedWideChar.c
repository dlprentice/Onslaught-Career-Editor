/* address: 0x005657f0 */
/* name: ControlsUI__WriteRepeatedWideChar */
/* signature: void __cdecl ControlsUI__WriteRepeatedWideChar(int param_1, int param_2, int param_3, void * param_4) */


void __cdecl ControlsUI__WriteRepeatedWideChar(int param_1,int param_2,int param_3,void *param_4)

{
  do {
    if (param_2 < 1) {
      return;
    }
    param_2 = param_2 + -1;
    ControlsUI__WriteWideCharAndCount(param_1,param_3,param_4);
  } while (*(int *)param_4 != -1);
  return;
}

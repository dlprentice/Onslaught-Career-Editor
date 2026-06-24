/* address: 0x0052c430 */
/* name: CD3DApplication__Cleanup3DEnvironment */
/* signature: void __fastcall CD3DApplication__Cleanup3DEnvironment(void * param_1) */


void __fastcall CD3DApplication__Cleanup3DEnvironment(void *param_1)

{
  char acStack_100 [256];

  *(undefined4 *)((int)param_1 + 0x32e48) = 0;
  *(undefined4 *)((int)param_1 + 0x32e4c) = 0;
  if (*(int *)((int)param_1 + 0x32ea0) != 0) {
    (**(code **)(*(int *)param_1 + 0x28))(0);
    if (DAT_0089c04c != (int *)0x0) {
      (**(code **)(*DAT_0089c04c + 8))(DAT_0089c04c);
      DAT_0089c04c = (int *)0x0;
    }
    (**(code **)(**(int **)((int)param_1 + 0x32ea0) + 8))(*(int **)((int)param_1 + 0x32ea0));
    (**(code **)(**(int **)((int)param_1 + 0x32e9c) + 8))(*(int **)((int)param_1 + 0x32e9c));
    sprintf(acStack_100,s_d3ddev_refcount__d_0064c3d8);
    DebugTrace(acStack_100);
    sprintf(acStack_100,s_d3d_refcount__d_0064c3c4);
    DebugTrace(acStack_100);
    *(undefined4 *)((int)param_1 + 0x32ea0) = 0;
    *(undefined4 *)((int)param_1 + 0x32e9c) = 0;
  }
  (**(code **)(*(int *)param_1 + 0x1c))();
  return;
}

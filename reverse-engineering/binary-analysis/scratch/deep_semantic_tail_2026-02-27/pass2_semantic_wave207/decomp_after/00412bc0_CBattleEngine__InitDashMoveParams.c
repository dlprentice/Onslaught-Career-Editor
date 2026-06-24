/* address: 0x00412bc0 */
/* name: CBattleEngine__InitDashMoveParams */
/* signature: void * __thiscall CBattleEngine__InitDashMoveParams(void * this, void * param_1, int param_2) */


void * __thiscall CBattleEngine__InitDashMoveParams(void *this,void *param_1,int param_2)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d1328;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  CSPtrSet__Init(this);
  *(void **)((int)this + 0x20) = param_1;
  local_4 = 0;
  *(undefined4 *)((int)this + 0x24) = 0xc0490fdb;
  *(undefined4 *)((int)this + 0x28) = 0xc0490fdb;
  *(undefined4 *)((int)this + 0x10) = 0;
  *(undefined4 *)((int)this + 0x18) = 0;
  *(undefined4 *)((int)this + 0x1c) = 0;
  CSPtrSet_Remove__Wrapper_004146b0(this);
  *(undefined4 *)((int)this + 0x14) = 1;
  *(undefined4 *)((int)this + 0x3c) = 0;
  *(undefined4 *)((int)this + 0x40) = 0;
  *(undefined4 *)((int)this + 0x2c) = 0xc1200000;
  *(undefined4 *)((int)this + 0x30) = 0xc1200000;
  *(undefined4 *)((int)this + 0x34) = 0xc1200000;
  *(undefined4 *)((int)this + 0x38) = 0xc1200000;
  *(undefined4 *)((int)this + 0x44) = 0;
  CConsole__RegisterVariable
            (s_g_dash_start_006238a8,s__default_0_9__When_the_dash_sepe_006238b8,4,&DAT_006236b0,0,0
            );
  CConsole__RegisterVariable
            (s_g_dash_end_00623844,s__default_0_8__When_the_dash_sepe_00623850,4,&DAT_006236b4,0,0);
  CConsole__RegisterVariable
            (s_g_dash_time_006237d4,s__default_0_2__Dash_move_kicks_of_006237e0,4,&DAT_006236ac,0,0)
  ;
  CConsole__RegisterVariable
            (s_g_dash_length_00623774,s__default_15__Number_of_game_turn_00623784,0,&DAT_006236b8,0,
             0);
  CConsole__RegisterVariable
            (s_g_dash_friction_0062370c,s__default_5__Number_of_game_turns_0062371c,0,&DAT_006236bc,
             0,0);
  CConsole__RegisterVariable
            (s_Ag_dash_velocity_006236c3 + 1,s__default_25_0__Initial_velocity_g_006236d4,4,
             &DAT_006236c0,0,0);
  ExceptionList = local_c;
  return this;
}

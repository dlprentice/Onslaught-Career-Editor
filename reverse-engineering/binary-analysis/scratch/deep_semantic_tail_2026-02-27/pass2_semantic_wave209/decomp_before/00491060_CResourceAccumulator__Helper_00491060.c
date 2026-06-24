/* address: 0x00491060 */
/* name: CResourceAccumulator__Helper_00491060 */
/* signature: void __thiscall CResourceAccumulator__Helper_00491060(void * this, int param_1, void * param_2) */


void __thiscall CResourceAccumulator__Helper_00491060(void *this,int param_1,void *param_2)

{
  undefined4 extraout_EAX;
  undefined4 extraout_EDX;
  void *extraout_EDX_00;
  int unaff_EDI;
  undefined4 local_24;
  char local_20 [32];

  CConsole__Status(&DAT_00663498,s_Deserializing_map_0062da84);
  CMeshPart__Helper_00423910(param_1);
  CMeshPart__Helper_00423960((void *)param_1,(int)&local_24,4,1,unaff_EDI);
  sprintf(local_20,s_Deserializing_map__d_0062da6c);
  DebugTrace(local_20);
  *(undefined4 *)((int)this + 0x93dc) = local_24;
  *(undefined4 *)((int)this + 0x93e4) = 1;
  *(undefined4 *)((int)this + 0x93e0) = 1;
  CHeightField__Load(param_1);
  CMixerMap__Init(param_1);
  CResourceAccumulator__Helper_0044a2a0
            (CONCAT31((int3)((uint)extraout_EDX >> 8),*(undefined1 *)((int)this + 0x1090)));
  CFrontEndPage__Process_NoOp
            ((void *)CONCAT31((int3)((uint)extraout_EAX >> 8),*(undefined1 *)((int)this + 0x1091)),
             unaff_EDI);
  CResourceAccumulator__Helper_0044a1f0(&DAT_0089c9a0,(uint)*(byte *)((int)this + 0x1030),unaff_EDI)
  ;
  CResourceAccumulator__Helper_0048dec0();
  CResourceAccumulator__Helper_0044a2c0(0x89c9a0,extraout_EDX_00);
  CConsole__StatusDone(&DAT_00663498,s_Deserializing_map_0062da84,'\x01');
  return;
}

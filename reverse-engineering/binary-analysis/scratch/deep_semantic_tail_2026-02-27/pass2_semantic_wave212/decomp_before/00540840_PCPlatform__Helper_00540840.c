/* address: 0x00540840 */
/* name: PCPlatform__Helper_00540840 */
/* signature: void __thiscall PCPlatform__Helper_00540840(void * this, int param_1, void * param_2) */


void __thiscall PCPlatform__Helper_00540840(void *this,int param_1,void *param_2)

{
  int iVar1;
  undefined4 uVar2;
  int unaff_EDI;

  CMeshPart__ReadHeaderPairAndResetByteCount(param_1);
  CMeshPart__ReadHeaderPairAndResetByteCount(param_1);
  iVar1 = CDXTexture__Deserialize(0,param_1);
  *(int *)((int)this + 0x170) = iVar1;
  *(int *)(iVar1 + 0xa4) = *(int *)(iVar1 + 0xa4) + 1;
  D3DBufferRegistry__MoveToFreeList(*(int *)((int)this + 0x170));
  CMeshPart__ReadHeaderPairAndResetByteCount(param_1);
  CMeshPart__ReadBlockAndAccumulateByteCount((void *)param_1,(int)this + 4,0x50,1,unaff_EDI);
  CMeshPart__ReadBlockAndAccumulateByteCount((void *)param_1,(int)this + 0x54,4,1,unaff_EDI);
  CMeshPart__ReadBlockAndAccumulateByteCount((void *)param_1,(int)this + 0x58,4,1,unaff_EDI);
  CMeshPart__ReadBlockAndAccumulateByteCount((void *)param_1,(int)this + 0x5c,0x100,1,unaff_EDI);
  CMeshPart__ReadBlockAndAccumulateByteCount((void *)param_1,(int)this + 0x160,4,1,unaff_EDI);
  CMeshPart__ReadBlockAndAccumulateByteCount((void *)param_1,(int)this + 0x164,4,1,unaff_EDI);
  CMeshPart__ReadHeaderPairAndResetByteCount(param_1);
  CMeshPart__ReadBlockAndAccumulateByteCount((void *)param_1,(int)this + 0x17c,4,1,unaff_EDI);
  CMeshPart__ReadBlockAndAccumulateByteCount((void *)param_1,(int)this + 0x180,0x1000,1,unaff_EDI);
  *(undefined1 *)((int)this + 0x15c) = 0;
  uVar2 = CVBufTexture__GetOrCreate(*(undefined4 *)((int)this + 0x170),0);
  *(undefined4 *)((int)this + 0x174) = uVar2;
  CVBufTexture__SetVBFormat(0x144,0x208,0x1c,4,0);
  CVBufTexture__SetIBFormat(0x65,0x208,2,0);
  return;
}

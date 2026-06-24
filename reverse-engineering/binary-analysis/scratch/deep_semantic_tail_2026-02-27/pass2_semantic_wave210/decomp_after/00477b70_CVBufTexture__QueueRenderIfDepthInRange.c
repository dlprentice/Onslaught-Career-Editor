/* address: 0x00477b70 */
/* name: CVBufTexture__QueueRenderIfDepthInRange */
/* signature: void __thiscall CVBufTexture__QueueRenderIfDepthInRange(void * this, void * param_1, void * param_2, float param_3) */


void __thiscall
CVBufTexture__QueueRenderIfDepthInRange(void *this,void *param_1,void *param_2,float param_3)

{
  if ((DAT_0089d680 == '\0') &&
     ((float)param_2 < *(float *)((int)this + *(int *)((int)this + 0x5bc) * 8 + 8))) {
    CRenderQueue__InsertSortedByDepth(this,param_1,(float)param_2);
  }
  return;
}

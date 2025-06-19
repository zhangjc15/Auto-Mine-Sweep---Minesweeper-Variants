import numpy as np
from scipy.ndimage import label

MINE=-1
HIDDEN=-2
NOT_MINE=-3

LEGAL=2
POSSIBLE=1
ILLEGAL=0

class mine_sweeper:

    def __init__(self, num_mines, map):
        self.num_mines=num_mines
        self.map=map.copy()
        self.num_rows=map.shape[0]
        self.num_cols=map.shape[1]
        self.legal=POSSIBLE
        self.legal_map=POSSIBLE*np.ones_like(map)

    def copy(self):
        new_self=mine_sweeper(self.num_mines,self.map)
        new_self.legal=self.legal
        new_self.legal_map=self.legal_map.copy()
        return new_self

    def coord_around(self,coord,self_include=False):
        x=coord[0]
        y=coord[1]

        retval=[]
        for r in range(x-1,x+2):
            for c in range(y-1,y+2):
                if r >= 0 and r < self.num_rows and c >= 0 and c < self.num_cols:
                    if r==x and c==y and self_include:
                        retval.append(np.array([r,c]))
                    else:
                        retval.append(np.array([r,c]))

        return retval
    
    def count_around(self,coord):
        cnt_mines=0
        cnt_hidden=0
        cnt_notmine=0

        coords_around=self.coord_around(coord,self_include=True)

        for coord_loop in coords_around:
            tmp=self.map[coord_loop[0],coord_loop[1]]
            if tmp>=0 or tmp==NOT_MINE:
                cnt_notmine=cnt_notmine+1
            elif tmp==HIDDEN:
                cnt_hidden=cnt_hidden+1
            elif tmp==MINE:
                cnt_mines=cnt_mines+1

        return cnt_mines,cnt_notmine,cnt_hidden
    
    def is_legal(self,coords_to_check=None):
        if not hasattr(self,'legal_map'):
            self.legal_map=POSSIBLE*np.ones((self.num_rows,self.num_cols),dtype=int)

        if not hasattr(self,'legal'):
            self.legal=POSSIBLE

        if coords_to_check is None:
            coords_to_check=[None]*(self.num_rows*self.num_cols)
            id=0
            for i in range(self.num_rows):
                for j in range(self.num_cols):
                    coords_to_check[id]=np.array([i,j],dtype=int)
                    id=id+1
        
        for coord in coords_to_check:
            cnt_mines,cnt_notmine,cnt_hidden=self.count_around(coord)

            tmp=self.map[coord[0],coord[1]]
            if tmp>=0:
                if cnt_mines>tmp or cnt_mines+cnt_hidden<tmp:
                    self.legal_map[coord[0],coord[1]]=ILLEGAL
                elif cnt_mines==tmp and cnt_hidden==0:
                    self.legal_map[coord[0],coord[1]]=LEGAL
                else:
                    self.legal_map[coord[0],coord[1]]=POSSIBLE
            
        total_mines=(self.map==MINE).sum()
        total_hidden=(self.map==HIDDEN).sum()

        if total_mines>self.num_mines or total_mines+total_hidden<self.num_mines:
            self.legal=ILLEGAL
            return
        
        if (self.legal_map==ILLEGAL).sum()>0:
            self.legal=ILLEGAL
            return
        
        if ((self.map<0) | (self.legal_map==LEGAL)).sum()==(self.num_rows*self.num_cols):
            # if every point that has a required number of mines around it has been satisfied
            self.legal=LEGAL
            return
        
        else:
            self.legal=POSSIBLE
            return
    
    def get_next_hidden_coord(self):
        # find a hidden box to try deducing whether it has mine or not
        # choose a point that has a known labeled number, and find the number of hidden boxes around it. Choose the smallest number of hidden boxes to keep the deduction
        min_hidden=9
        coord=[]

        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.map[i,j]>0:
                    _,_,cnt_hidden=self.count_around([i,j])
                    if cnt_hidden>0 and cnt_hidden<min_hidden:
                        min_hidden=cnt_hidden
                        coords_around=self.coord_around([i,j],self_include=False)
                        for coord_search in coords_around:
                            if self.map[coord_search[0],coord_search[1]]==HIDDEN:
                                coord=coord_search
                                break
        
        if len(coord)==0:
            print('unexpected behavior when obtaining next hidden box')

        return coord                        

    def first_order_deduct(self,coords_to_check=None):
        # use first order logic to make logical deduction based on the
        # current map, and update it, coords_to_check will store the coordinates of
        # the places to perform deductions

        if coords_to_check is None:
            # by default, perform deduction for every possible point that has known number of mines around
            cnt_known=(self.map>=0).sum()
            
            coords_to_check=[None]*cnt_known

            id=0
            for i in range(self.num_rows):
                for j in range(self.num_cols):
                    if self.map[i,j]>=0:
                        coords_to_check[id]=np.array([i,j])
                        id=id+1

        flag_change=False
        self.is_legal(coords_to_check)
        if self.legal==ILLEGAL:
            return flag_change
        elif self.legal==LEGAL:
            return flag_change
        
        for coord in coords_to_check:
            num_mines_around=self.map[coord[0],coord[1]]

            if num_mines_around>=0:
                r=coord[0]
                c=coord[1]

                cnt_mines,cnt_notmine,cnt_hidden=self.count_around(coord)

                if cnt_mines==num_mines_around:
                    coords_around=self.coord_around(coord,self_include=False)
                    for coord_update in coords_around:
                        if self.map[coord_update[0],coord_update[1]]==HIDDEN:
                            self.map[coord_update[0],coord_update[1]]=NOT_MINE
                            flag_change=True
                            coord_new=self.coord_around(coord_update)
                            if not len(coord_new)==0:
                                self.first_order_deduct(coord_new)
                                if self.legal==ILLEGAL:
                                    return
                                
                elif cnt_mines+cnt_hidden==num_mines_around:
                    coords_around=self.coord_around(coord,self_include=False)
                    for coord_update in coords_around:
                        if self.map[coord_update[0],coord_update[1]]==HIDDEN:
                            self.map[coord_update[0],coord_update[1]]=MINE
                            flag_change=True
                            coord_new=self.coord_around(coord_update)
                            if not len(coord_new)==0:
                                self.first_order_deduct(coord_new)
                                if self.legal==ILLEGAL:
                                    return
        
        total_mines=(self.map==MINE).sum()
        total_hidden=(self.map==HIDDEN).sum()

        if total_mines==self.num_mines:
            self.map[self.map==HIDDEN]=NOT_MINE
            self.is_legal()
            flag_change=True
        elif total_mines+total_hidden==self.num_mines:
            self.map[self.map==HIDDEN]=MINE
            self.is_legal()
            flag_change=True
    
        return flag_change
    
    def recursion_deduct(self,coords_to_check=None):
        # recursively deduce whether the given status is possible
        if coords_to_check is None:
            # by default, perform deduction for every possible point that has known number of mines around
            cnt_known=(self.map>=0).sum()
            
            coords_to_check=[None]*cnt_known

            id=0
            for i in range(self.num_rows):
                for j in range(self.num_cols):
                    if self.map[i,j]>=0:
                        coords_to_check[id]=np.array([i,j])
                        id=id+1
    
        self.first_order_deduct(coords_to_check)
        if self.legal==ILLEGAL:
            possible=False
            return possible
        elif self.legal==LEGAL:
            possible=True
            return possible
        else:
            coord_hidden=self.get_next_hidden_coord()
            coords_around=self.coord_around(coord_hidden,self_include=False)
            coords_to_check=[]
            for coord in coords_around:
                if self.map[coord[0],coord[1]]>0:
                    coords_to_check.append(coord)
            
            new_self_1=self.copy()
            new_self_1.map[coord_hidden[0],coord_hidden[1]]=NOT_MINE
            p2=new_self_1.recursion_deduct(coords_to_check)
            if p2==True:
                possible=True
                return possible
            else:
                del new_self_1
                self.map[coord_hidden[0],coord_hidden[1]]=MINE
                p3=self.recursion_deduct(coords_to_check)
                if p3==True:
                    possible=True
                    return possible
                else:
                    possible=False
                    return possible

    def update_deduct(self,if_print=True):
        list_open=[]
        list_mark_mine=[]
        old_map=self.map.copy()
        flag_change=False

        flag1=self.first_order_deduct()

        if flag1==True:
            flag_change=True
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.map[i,j]==HIDDEN:
                    around_known_box=False
                    coords_around=self.coord_around(np.array([i,j]),self_include=False)
                    for coord in coords_around:
                        if self.map[coord[0],coord[1]]>0:
                            around_known_box=True
                            break

                    if around_known_box:
                        new_self_1=self.copy()
                        new_self_2=self.copy()

                        new_self_1.map[i,j]=MINE
                        new_self_2.map[i,j]=NOT_MINE

                        p1=new_self_1.recursion_deduct(coords_around)
                        p2=new_self_2.recursion_deduct(coords_around)

                        if p1 and not(p2):
                            self.map=new_self_1.map.copy()
                            self.legal_map=new_self_1.legal_map.copy()
                            self.legal=new_self_1.legal
                            flag_change=True
                        elif not(p1) and p2:
                            self.map=new_self_2.map.copy()
                            self.legal_map=new_self_2.legal_map.copy()
                            self.legal=new_self_2.legal
                            flag_change=True
                        elif not(p1) and not(p2):
                            flag_change=True
                            self.legal=ILLEGAL
                            return flag_change
                        
                        del new_self_1
                        del new_self_2

        new_map=self.map.copy()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if not old_map[i,j]==new_map[i,j]:
                    if new_map[i,j]==NOT_MINE:
                        list_open.append(np.array([i,j]))
                        if if_print:
                            print("box ({},{}): ".format(i, j), end='')
                            print('open')
                    elif new_map[i,j]==MINE:
                        list_mark_mine.append(np.array([i,j]))
                        if if_print:
                            print("box ({},{}): ".format(i, j), end='')
                            print('mark as mine')            
            
        if not flag_change:
            for i in range(self.num_rows):
                for j in range(self.num_cols):
                    if self.map[i,j]==HIDDEN:
                        around_known_box=False
                        coords_around=self.coord_around(np.array([i,j]),self_include=False)
                        for coord in coords_around:
                            if self.map[coord[0],coord[1]]>0:
                                around_known_box=True
                                break

                        if not around_known_box:
                            new_self_1=self.copy()
                            new_self_2=self.copy()

                            new_self_1.map[i,j]=MINE
                            new_self_2.map[i,j]=NOT_MINE

                            p1=new_self_1.recursion_deduct(coords_around)
                            p2=new_self_2.recursion_deduct(coords_around)

                            if p1 and not(p2):
                                self.map=new_self_1.map.copy()
                                self.legal_map=new_self_1.legal_map.copy()
                                self.legal=new_self_1.legal
                                flag_change=True
                            elif not(p1) and p2:
                                self.map=new_self_2.map.copy()
                                self.legal_map=new_self_2.legal_map.copy()
                                self.legal=new_self_2.legal
                                flag_change=True
                            elif not(p1) and not(p2):
                                flag_change=True
                                self.legal=ILLEGAL
                                return flag_change
                            
                            del new_self_1
                            del new_self_2

            new_map=self.map.copy()
            for i in range(self.num_rows):
                for j in range(self.num_cols):
                    if not old_map[i,j]==new_map[i,j]:
                        if new_map[i,j]==NOT_MINE:
                            list_open.append(np.array([i,j]))
                            if if_print:
                                print("box ({},{}): ".format(i, j), end='')
                                print('open')
                        elif new_map[i,j]==MINE:
                            list_mark_mine.append(np.array([i,j]))
                            if if_print:
                                print("box ({},{}): ".format(i, j), end='')
                                print('mark as mine')
        
        # if no remaining hidden boxes exist, then the game has been solved
        cnt_hidden_tot=(self.map==HIDDEN).sum()
        if cnt_hidden_tot==0:
            flag_change=2

        return flag_change,list_open,list_mark_mine

class mine_sweeper_quad(mine_sweeper):
    def __init__(self,num_mines,map):
        super(mine_sweeper_quad,self).__init__(num_mines,map)
        self.legal_quad_map=POSSIBLE*np.ones((self.num_rows-1,self.num_cols-1))
        self.legal_quad=POSSIBLE
    def copy(self):
        new_self=mine_sweeper_quad(self.num_mines,self.map)
        new_self.legal=self.legal
        new_self.legal_map=self.legal_map.copy()
        new_self.legal_quad_map=self.legal_quad_map.copy()
        new_self.legal_quad=self.legal_quad
        return new_self
    
    def quad_around(self,coord):
        quads_around=[]
        for i in range(2):
            for j in range(2):
                quad_coord = np.array([coord[0] - i, coord[1] - j],dtype=int)
                if quad_coord[0] >= 0 and quad_coord[1] >= 0 and quad_coord[0] < self.num_rows - 1 and quad_coord[1] < self.num_cols - 1:
                    quads_around.append(quad_coord)
        return quads_around
    
    def get_next_undecided_quad(self):
        min_hidden=5
        iq,jq=np.where(self.legal_quad_map==POSSIBLE)
        quad_next=None
        for i,j in zip(iq,jq):
            map_local=self.map[i:i+2,j:j+2]
            cnt_hidden=(map_local==HIDDEN).sum()
            if cnt_hidden<min_hidden:
                quad_next=np.array([i,j],dtype=int)
                min_hidden=cnt_hidden
        
        return quad_next
    
    def is_legal_quad(self,quads_to_check=None):
        if (self.map==MINE).sum()==self.num_mines:
            self.map[self.map==HIDDEN]=NOT_MINE
            quads_to_check=None
        if quads_to_check is None:
            quads_to_check=[]
            for i in range(self.num_rows-1):
                for j in range(self.num_cols-1):
                    quads_to_check.append(np.array([i,j]))
        
        for quad in quads_to_check:
            tmp=self.map[quad[0]:quad[0]+2,quad[1]:quad[1]+2]
            cnt_mines=(tmp==MINE).sum()
            cnt_hidden=(tmp==HIDDEN).sum()
            if cnt_mines>0:
                self.legal_quad_map[quad[0],quad[1]]=LEGAL
            elif cnt_hidden>0:
                self.legal_quad_map[quad[0],quad[1]]=POSSIBLE
            else:
                self.legal_quad_map[quad[0],quad[1]]=ILLEGAL

        if (self.legal_quad_map==ILLEGAL).sum()>0 or (self.map==MINE).sum()>self.num_mines:
            self.legal_quad=ILLEGAL
            return
        elif (self.legal_quad_map!=LEGAL).sum()==0:
            self.legal_quad=LEGAL
            return
        
    def is_legal_quad_recursive(self):
        # recursively judge whether the given constraints for quads is possible to satisfy
        # the constraint of opened numbers will not be considered
        '''
        if quads_to_check is None:
            yq,xq=np.where(self.legal_quad_map==POSSIBLE)
            quads_to_check = [np.array([y, x]) for y, x in zip(yq, xq)]
              
        for quad in quads_to_check:
            map_local=self.map[quad[0]:quad[0]+1,quad[1]:quad[1]+1]
            cnt_mines=(map_local==MINE).sum()
            cnt_hidden=(map_local==HIDDEN).sum()
            if cnt_mines==0 and cnt_hidden==0:
                self.legal_quad_map[quad[0],quad[1]]=ILLEGAL
            elif cnt_mines>0:
                self.legal_quad_map[quad[0],quad[1]]=LEGAL
        '''
        if (self.legal_quad_map==ILLEGAL).sum()>0:
            self.legal_quad=ILLEGAL
            #self.legal=ILLEGAL
            return
        elif (self.map==MINE).sum()>self.num_mines:
            self.legal_quad=ILLEGAL
            #self.legal=ILLEGAL
            return
        elif (self.legal_quad_map!=LEGAL).sum()==0:
            self.legal_quad=LEGAL
            return
        
        quad_next=self.get_next_undecided_quad()
        max_neigh=0
        for a in range(2):
            for b in range(2):
                if self.map[quad_next[0]+a,quad_next[1]+b]==HIDDEN:
                    cnt_neigh=0
                    quads_around=self.quad_around(np.array([quad_next[0]+a,quad_next[1]+b],dtype=int))
                    quads_tmp=[]
                    for quad in quads_around:
                        if self.legal_quad_map[quad[0],quad[1]]==POSSIBLE:
                            cnt_neigh+=1
                            quads_tmp.append(quad)
                
                    if cnt_neigh>max_neigh:
                        max_neigh=cnt_neigh
                        quads_to_check_next=quads_tmp
                        coord_change=np.array([quad_next[0]+a,quad_next[1]+b],dtype=int)
        
        new_self=self.copy()
        new_self.map[coord_change[0],coord_change[1]]=MINE
        new_self.is_legal_quad(quads_to_check_next)
        new_self.is_legal_quad_recursive()
        if new_self.legal_quad==LEGAL:
            self.legal_quad=LEGAL
            return
        elif new_self.legal_quad==ILLEGAL:
            del new_self
            new_self=self.copy()
            new_self.map[coord_change[0],coord_change[1]]=NOT_MINE
            new_self.is_legal_quad(quads_to_check_next)
            new_self.is_legal_quad_recursive()
            if new_self.legal_quad==LEGAL:
                self.legal_quad=LEGAL
                return
            elif new_self.legal_quad==ILLEGAL:
                self.legal_quad=ILLEGAL
                #self.legal=ILLEGAL
                return
            else:
                print('unexpected return value from mine_sweeper_quad::is_legal_quad_recursive()')
        else:
            print('unexpected return value from mine_sweeper_quad::is_legal_quad_recursive()')
    
    def is_legal(self,coords_to_check=None,quads_to_check=None):
        super(mine_sweeper_quad,self).is_legal(coords_to_check)
        
        
        self.is_legal_quad(quads_to_check)
        '''
        if (self.legal_quad_map==ILLEGAL).sum()>0:
            self.legal_quad=ILLEGAL
        elif (self.legal_quad_map==LEGAL).sum()==self.legal_quad_map.size:
            self.legal_quad=LEGAL
        else:
            self.legal_quad=POSSIBLE
        
        if self.legal==ILLEGAL or self.legal_quad==ILLEGAL:
            self.legal=ILLEGAL
            return
        elif self.legal==LEGAL and self.legal_quad==LEGAL:
            self.legal=LEGAL
            return
        else:
            self.legal=POSSIBLE
            return
        '''

        
        if (self.legal_quad_map==ILLEGAL).sum()>0:
            self.legal_quad=ILLEGAL
        
        if self.legal==ILLEGAL or self.legal_quad==ILLEGAL:

            return
        # after every numbered box has been satisfied, then consider the possibilities of arranging the remaining mines to satisfies every quad's constraint
        if self.legal==LEGAL:
            self.is_legal_quad_recursive()

    def first_order_deduct(self, coords_to_check=None,quads_to_check=None):
        if coords_to_check is None:
            # by default, perform deduction for every possible point that has known number of mines around
            cnt_known=(self.map>=0).sum()
            
            coords_to_check=[None]*cnt_known

            id=0
            for i in range(self.num_rows):
                for j in range(self.num_cols):
                    if self.map[i,j]>=0:
                        coords_to_check[id]=np.array([i,j])
                        id=id+1

        if quads_to_check is None:
            quads_to_check=[]
            for i in range(self.num_rows-1):
                for j in range(self.num_cols-1):
                    quads_to_check.append(np.array([i,j]))

        flag_change=False
        self.is_legal(coords_to_check,quads_to_check)

        if self.legal==ILLEGAL or self.legal_quad==ILLEGAL:
            return flag_change
        elif self.legal==LEGAL and self.legal_quad==LEGAL:
            return flag_change
        
        for coord in coords_to_check:
            num_mines_around=self.map[coord[0],coord[1]]

            if num_mines_around>=0:

                cnt_mines,cnt_notmine,cnt_hidden=self.count_around(coord)

                if cnt_mines==num_mines_around:
                    coords_around=self.coord_around(coord,self_include=False)
                    for coord_update in coords_around:
                        if self.map[coord_update[0],coord_update[1]]==HIDDEN:
                            self.map[coord_update[0],coord_update[1]]=NOT_MINE
                            flag_change=True
                            coord_new=self.coord_around(coord_update)
                            quads_new=self.quad_around(coord_update)
                            if not len(coord_new)==0 or not len(quads_new)==0:
                                self.first_order_deduct(coord_new,quads_new)
                                if self.legal==ILLEGAL or self.legal_quad==ILLEGAL:
                                    return flag_change
                                
                elif cnt_mines+cnt_hidden==num_mines_around:
                    coords_around=self.coord_around(coord,self_include=False)
                    for coord_update in coords_around:
                        if self.map[coord_update[0],coord_update[1]]==HIDDEN:
                            self.map[coord_update[0],coord_update[1]]=MINE
                            flag_change=True
                            coord_new=self.coord_around(coord_update)
                            quads_new=self.quad_around(coord_update)
                            if not len(coord_new)==0 or not len(quads_new)==0:
                                self.first_order_deduct(coord_new,quads_new)
                                if self.legal==ILLEGAL or self.legal_quad==ILLEGAL:
                                    return flag_change
        
        for quad in quads_to_check:
            if self.legal_quad_map[quad[0],quad[1]]==POSSIBLE:
                map_local=self.map[quad[0]:quad[0]+2,quad[1]:quad[1]+2]
                num_not_mine_quad=(map_local==NOT_MINE).sum()
                if num_not_mine_quad==3:
                    coord_update=[]
                    flag_break=False
                    for a in range(2):
                        for b in range(2):
                            if map_local[a,b]==HIDDEN:
                                coord_update=np.array([quad[0]+a,quad[1]+b],dtype=int)
                                flag_break=True
                                break
                        if flag_break:
                            break
                    
                    if len(coord_update)==0:
                        print('unexpected behavior in mine_sweeper_quad::first_order_deduct() during quad deductions')
                    else:
                        self.map[coord_update[0],coord_update[1]]=MINE
                        flag_change=True
                        coord_new=self.coord_around(coord_update)
                        quads_new=self.quad_around(coord_update)
                        if not len(coord_new)==0 or not len(quads_new)==0:
                            self.first_order_deduct(coord_new,quads_new)
                            if self.legal==ILLEGAL or self.legal_quad==ILLEGAL:
                                return flag_change
        total_mines=(self.map==MINE).sum()
        total_hidden=(self.map==HIDDEN).sum()

        if total_mines==self.num_mines:
            self.map[self.map==HIDDEN]=NOT_MINE
            self.is_legal()
            flag_change=True
        elif total_mines+total_hidden==self.num_mines:
            self.map[self.map==HIDDEN]=MINE
            self.is_legal()
            flag_change=True
        
        return flag_change

    def recursion_deduct(self, coords_to_check=None,quads_to_check=None):
         # recursively deduce whether the given status is possible
        if coords_to_check is None:
            # by default, perform deduction for every possible point that has known number of mines around
            cnt_known=(self.map>=0).sum()
            
            coords_to_check=[None]*cnt_known

            id=0
            for i in range(self.num_rows):
                for j in range(self.num_cols):
                    if self.map[i,j]>=0:
                        coords_to_check[id]=np.array([i,j])
                        id=id+1

        if quads_to_check is None:
            quads_to_check=[]
            for i in range(self.num_rows-1):
                for j in range(self.num_cols-1):
                    quads_to_check.append(np.array([i,j]))

        self.first_order_deduct(coords_to_check,quads_to_check)

        if self.legal==ILLEGAL or self.legal_quad==ILLEGAL:
            possible=False
            return possible
        elif self.legal==LEGAL and self.legal_quad==LEGAL:
            possible=True
            return possible
        else:
            coord_hidden=self.get_next_hidden_coord()
            if len(coord_hidden)==0:
                print('unexpected behavior in mine_sweeper_quad::recursion_deduct, coord_hidden is empty')
            coords_around=self.coord_around(coord_hidden,self_include=False)
            coords_to_check=[]
            for coord in coords_around:
                if self.map[coord[0],coord[1]]>0:
                    coords_to_check.append(coord)
            
            quads_around=self.quad_around(coord_hidden)
            quads_to_check=[]
            for quad in quads_around:
                if self.legal_quad_map[quad[0],quad[1]]==POSSIBLE:
                    quads_to_check.append(quad)
            

            new_self_1=self.copy()
            new_self_1.map[coord_hidden[0],coord_hidden[1]]=NOT_MINE
            p2=new_self_1.recursion_deduct(coords_to_check,quads_to_check)
            if p2==True:
                possible=True
                return possible
            else:
                del new_self_1
                self.map[coord_hidden[0],coord_hidden[1]]=MINE
                p3=self.recursion_deduct(coords_to_check,quads_to_check)
                if p3==True:
                    possible=True
                    return possible
                else:
                    possible=False
                    return possible

class mine_sweeper_connected(mine_sweeper):
    # connected模式：所有的雷都要以8连接方式相互连通
    def __init__(self, num_mines, map):
        super().__init__(num_mines, map)
        self.potential_mine = np.zeros((self.num_rows, self.num_cols), dtype=int)
        self.potential_mine[self.map == MINE] = 1
        self.potential_mine[self.map == HIDDEN] = 1
        self.num_labels, self.label_map = label(self.potential_mine, structure=np.ones((3, 3)))
    
    def is_legal(self, coords_to_check=None):
        super().is_legal(coords_to_check)
        if self.legal == ILLEGAL:
            return
        
        if self.num_labels > 1:
            has_mine = np.zeros(self.num_labels, dtype=int)
            for i in range(self.num_labels):
                has_mine[i] = np.any((self.label_map == i + 1) & (self.map == MINE))
            if np.sum(has_mine) > 1:
                self.legal = ILLEGAL
                return
    
    def update_one_not_mine(self, coord):
        # 更新一个HIDDEN格子为NOT_MINE
        if self.map[coord[0], coord[1]] != HIDDEN:
            print(f"Error: Trying to update a non-HIDDEN cell at {coord}.")
            return
        
        self.map[coord[0], coord[1]] = NOT_MINE
        self.potential_mine[coord[0], coord[1]] = 0
        
        # 快速检查是否需要重新标记连通区域
        # 如果当前格子相邻的雷区依然连通，则不需要重新标记

        r_min = max(coord[0] - 1, 0)
        r_max = min(coord[0] + 1, self.num_rows - 1)
        c_min = max(coord[1] - 1, 0)
        c_max = min(coord[1] + 1, self.num_cols - 1)

        sub_potential = self.potential_mine[r_min:r_max + 1, c_min:c_max + 1]
        num_sub_labels, sub_label_map = label(sub_potential, structure=np.ones((3, 3)))

        if num_sub_labels == 1:
            # 如果相邻区域仍然连通，则不需要重新标记
            return
        else:
            # 重新标记所有连通区域
            self.num_labels, self.label_map = label(self.potential_mine, structure=np.ones((3, 3)))
            return



if __name__=='__main__':
    num_mines = 5
    map = np.array([[-2,  1,  2,  1,-2],
                    [-2, -2, -2, -2,-2],
                    [-3, -2, -2, -2,-2],
                    [ 1, -3,  1, -2,-2]])

    print('原始局面:')
    print(map)
    ms = mine_sweeper(num_mines, map)
    ms.first_order_deduct()
    print('一阶推理后的局面：')
    print(ms.map)

    result, list_open, list_mark = ms.update_deduct()
    print('全自动推理后的局面：')
    print(ms.map)
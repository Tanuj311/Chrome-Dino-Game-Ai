import pygame, random
import neat, os
pygame.init()

WIN_WIDTH = 800
WIN_HEIGHT = 400
win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
clock = pygame.time.Clock()

dino_list = [pygame.image.load('dino1.png'), pygame.image.load('dino2.png'), pygame.image.load('dino3.png')]

cactus_list = [pygame.image.load('cactus.png'), pygame.image.load('3cactus.png'), pygame.image.load('bigcactus.png'), pygame.image.load('cactus1.png')]

bird_list = [pygame.image.load('bird1.png'), pygame.image.load('bird2.png')]

dino_duck_list = [pygame.image.load('dinoduck1.png'), pygame.image.load('dinoduck2.png')]

base_img = pygame.image.load('base.png')

gen = 0

class Dino:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 60
        self.vel = 2
        self.jump_count = 10
        self.jumping = False
        self.neg = 0
        self.img_count = 0
        self.img_count1= 0
        self.duck = False

    def jump(self):
        self.jumping = True
    
    def move(self):
        if self.jump_count >= -10:
            self.neg = 1
            if self.jump_count < 0:
                self.neg = -1
            self.y -= int((self.jump_count)**2*0.4*self.neg)
            self.jump_count-=1
        else:
            self.jump_count = 10
            self.jumping = False

    def draw(self):
        if not self.duck:
            win.blit(dino_list[int(self.img_count/10)-1],(self.x,self.y))
            if self.img_count < 30:
                self.img_count += 1
            if self.img_count >= 30:
                self.img_count = 0
        if self.duck:
            win.blit(dino_duck_list[int(self.img_count1/10)-1],(self.x, 290 - dino_duck_list[0].get_height()+5))
            if self.img_count1 < 30:
                self.img_count1 += 1
            if self.img_count1 >= 30:
                self.img_count1 = 0

    def get_mask(self):
        if not self.duck:
            dino_mask = pygame.mask.from_surface(dino_list[int(self.img_count/10)-1])
        if self.duck:
            dino_mask = pygame.mask.from_surface(dino_duck_list[0])
        return dino_mask

class Obs:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 8
        self.choose = random.randint(1,4)
       
    def move(self):
        self.x -= self.vel

    def draw(self):
        if self.choose == 1:
            win.blit(cactus_list[0], (int(self.x), 290-40))
        if self.choose == 2:
            win.blit(cactus_list[1], (int(self.x), 290-40))
        if self.choose == 3:
            win.blit(cactus_list[2], (int(self.x), 290 - cactus_list[2].get_height()+10))
        if self.choose == 4:
            win.blit(cactus_list[3], (int(self.x), 290-40))

    def collide(self, dino, birds):
        obs_mask = pygame.mask.from_surface(cactus_list[self.choose-1])
        dino_mask = dino.get_mask()
        if dino.duck:
            y = 290 - dino_duck_list[0].get_height()+5
        else:
            y = dino.y
        if len(birds) == 1:
            bird_mask = birds[0].get_mask()
            if birds[0].choose == 0:
                bird_offset = (int(birds[0].x - dino.x), int(birds[0].y - y))
            if birds[0].choose == 1:
                bird_offset = (int(birds[0].x - dino.x), int(birds[0].y1 - y))

            bird_point = dino_mask.overlap(bird_mask, bird_offset)

            if bird_point:
                return True

        if self.choose == 3:
            offset = (int(self.x - dino.x), int(self.y - cactus_list[2].get_height()+10 - y))
        else:
            offset = (int(self.x - dino.x), int(250 - y))

        point = dino_mask.overlap(obs_mask, offset)

        if point:
            return True
        
        return False

class Bird:
    def __init__(self, x,y):
        self.x = x
        self.y = y
        self.vel = 8
        self.img_count = 0
        self.img_count1 = 0
        self.y1 = self.y - 50
        self.choose = random.randint(0,1)

    def move(self):
        self.x -= self.vel

    def draw(self):
        if self.choose == 0:
            win.blit(bird_list[int(self.img_count/20)], (int(self.x), self.y))
            self.img_count += 1
            if self.img_count >= 40:
                self.img_count = 0
        if self.choose == 1:
            win.blit(bird_list[int(self.img_count1/20)], (int(self.x), self.y1))
            self.img_count1 += 1
            if self.img_count1 >= 40:
                self.img_count1 = 0
            
    def get_mask(self):
        bird_mask = pygame.mask.from_surface(bird_list[int(self.img_count/20)])
        return bird_mask

class Base:
    def __init__(self):
        self.x1 = 0
        self.x2 = base_img.get_width()
        self.y = 260
        self.vel = 8
        self.base_list = [base_img, base_img]
        self.width = self.base_list[0].get_width()
    
    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel
        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self):
        win.blit(self.base_list[0], (int(self.x1), self.y))
        win.blit(self.base_list[1], (int(self.x2), self.y))

def display_score(score):
    font = pygame.font.Font(None, 30)
    text = font.render(f'SCORE: {int(score)}',True, (0,0,0))
    win.blit(text, (10,10))

def main(genomes, config):
    global gen
    dinos = []
    obs = [Obs(WIN_WIDTH, 290)]
    birds = []
    score = 0
    base = Base()
    ge = []
    nets = []
    gen += 1


    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        dinos.append(Dino(60, 235))
        nets.append(net)
        ge.append(g)
        g.fitness = 0

    while True and len(dinos) > 0:
        win.fill((255,255,255))
        clock.tick(50)
        display_score(score)

        for o in obs:
            o.move()
            o.draw()
            if o.x < -50:
                obs.pop(obs.index(o))
            
            if obs[-1].x < WIN_WIDTH:
                obs_gap = random.randint(350, 500)
                obs.append(Obs(WIN_WIDTH + obs_gap, 290))

            if obs_gap >= 450:
                if len(birds) < 1:
                    birds.append(Bird(WIN_WIDTH+obs_gap/2, 215))
            if len(birds) > 0:
                if obs[-1].x - birds[0].x < 200:
                    obs.pop(-1)

        for b in birds:
            if b.x + bird_list[0].get_width() < 0:
                birds.pop(birds.index(b))
            b.move()
            b.draw()

        for x, dino in enumerate(dinos):
            if len(birds)> 0:
                if birds[0].x < dino.x and dino.jumping or dino.duck:
                    ge[x].fitness += 5
            for o in obs:
                if o.x < dino.x:
                    ge[x].fitness += 5
  
                if o.collide(dino, birds):
                    try:
                        dinos.pop(x)
                        nets.pop(x)
                        ge.pop(x)
                    except Exception as e:
                        pass
  
        for x, dino in enumerate(dinos):

            index = 0 
            
            obs_dist = abs(obs[index].x - dino.x)

            if len(birds) > 0 and obs[0].x < dino.x:
                obs_dist = birds[0].x - dino.x
            
            if len(birds) > 0 and birds[0].x < dino.x:
                obs_dist = obs[index].x - dino.x 

            if len(birds) > 0:
                if birds[0].choose == 0:
                    bird_y = birds[0].y 
                else:
                    bird_y = birds[0].y1
            else:
                bird_y = 0

            output = nets[x].activate((dino.y ,obs_gap, obs_dist, bird_y, int(base.vel)))
            i = output.index(max(output))
            
            dino.duck = False
            if i == 0:
                if not dino.jumping:
                    dino.jump()
            if dino.jumping:
                dino.move() 
            if i == 1:
                if not dino.jumping:
                    dino.duck =True
            dino.draw()

        base.move()
        base.draw()        

        score += 1/50
        for x, dino in enumerate(dinos):
            ge[x].fitness += 0.01

        if score > 5:
            for o in obs:
                o.vel += 0.1
            if base.vel < 100:
                base.vel += 0.1
            for b in birds:
                b.vel += 0.1

        font = pygame.font.Font(None, 30)
        text1 = font.render(f'GEN: {gen}', True, (0,0,0))
        win.blit(text1, (WIN_WIDTH-80,10))

        text2 = font.render(f'DINOS ALIVE: {len(dinos)}', True, (0,0,0))
        win.blit(text2, (WIN_WIDTH-180, 40))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                    config_path)
    
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
  

    winner = p.run(main, 50)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
